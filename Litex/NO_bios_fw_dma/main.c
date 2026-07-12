#include <stdbool.h>
#include <stdint.h>
#include <generated/csr.h>

#define WS2812_HW_LEDS       64u
#define WS2812_FRAME_BYTES   (WS2812_HW_LEDS * 3u)
#define WS2812_SHOW_TIMEOUT  1000000u
#define WS2812_DMA_TIMEOUT   1000000u

#define PROTO_SOF0           0xa5u
#define PROTO_SOF1           0x5au
#define PROTO_VERSION        0x01u
#define PROTO_MAX_PAYLOAD    192u

#define CMD_PING             0x01u
#define CMD_GET_INFO         0x02u
#define CMD_SET_FRAME        0x10u
#define CMD_CLEAR            0x11u
#define CMD_SET_BRIGHTNESS   0x12u
#define CMD_STOP             0x13u
#define CMD_ACK              0x7eu
#define CMD_NACK             0x7fu

#define STATUS_OK                    0u
#define STATUS_CRC_ERROR             1u
#define STATUS_INVALID_LENGTH        2u
#define STATUS_UNKNOWN_COMMAND       3u
#define STATUS_DEVICE_BUSY           4u
#define STATUS_DMA_TIMEOUT           5u
#define STATUS_WS2812_TIMEOUT        6u
#define STATUS_PROTOCOL_VERSION      7u

static volatile uint32_t ws2812_buffer[WS2812_HW_LEDS] __attribute__((aligned(4)));

static uint8_t rx_payload[PROTO_MAX_PAYLOAD];
static uint8_t rx_command;
static uint16_t rx_sequence;
static uint16_t rx_length;
static uint16_t rx_crc;
static uint16_t rx_index;
static uint8_t brightness = 255u;

typedef enum {
    WAIT_SOF_1 = 0,
    WAIT_SOF_2,
    READ_VERSION,
    READ_COMMAND,
    READ_SEQUENCE_0,
    READ_SEQUENCE_1,
    READ_LENGTH_0,
    READ_LENGTH_1,
    READ_PAYLOAD,
    READ_CRC_0,
    READ_CRC_1,
} parser_state_t;

static parser_state_t parser_state = WAIT_SOF_1;
static uint16_t parser_crc;

static void ws2812_delay(unsigned int cycles)
{
    volatile unsigned int i;

    for (i = 0; i < cycles; i++) {
        __asm__ volatile("nop");
    }
}

static uint32_t ws2812_pack_rgb(uint8_t r, uint8_t g, uint8_t b)
{
    return ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
}

static void ws2812_set_pixel_word(uint32_t index, uint32_t word)
{
    if (index >= WS2812_HW_LEDS) {
        return;
    }

    ws2812_buffer[index] = word & 0x00ffffffu;
}

static void ws2812_set_pixel(uint32_t index, uint8_t r, uint8_t g, uint8_t b)
{
    ws2812_set_pixel_word(index, ws2812_pack_rgb(r, g, b));
}

static void ws2812_fill(uint8_t r, uint8_t g, uint8_t b)
{
    uint32_t i;

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        ws2812_set_pixel(i, r, g, b);
    }
}

static bool wait_until_loader_done(uint32_t timeout)
{
    while (disp0_loader_done_read() == 0) {
        if (timeout-- == 0) {
            return false;
        }
        ws2812_delay(10);
    }

    return true;
}

static bool wait_until_dma_done(uint32_t timeout)
{
    while (disp0_dma_done_read() == 0) {
        if (timeout-- == 0) {
            return false;
        }
        ws2812_delay(10);
    }

    return true;
}

static bool wait_until_ws2812_done(uint32_t timeout)
{
    while (disp0_done_read() == 0) {
        if (timeout-- == 0) {
            return false;
        }
        ws2812_delay(10);
    }

    return true;
}

static bool wait_until_ws2812_busy_starts(uint32_t timeout)
{
    while (disp0_done_read() != 0) {
        if (timeout-- == 0) {
            return false;
        }
        ws2812_delay(10);
    }

    return true;
}

static bool ws2812_load_framebuffer(void)
{
    disp0_dma_enable_write(0);
    disp0_dma_loop_write(0);

    disp0_loader_start_write(1);
    disp0_dma_base_write((uint32_t)(uintptr_t)ws2812_buffer);
    disp0_dma_length_write(WS2812_HW_LEDS * 4u);
    disp0_dma_enable_write(1);

    if (!wait_until_loader_done(WS2812_DMA_TIMEOUT)) {
        disp0_dma_enable_write(0);
        return false;
    }

    if (!wait_until_dma_done(WS2812_DMA_TIMEOUT)) {
        disp0_dma_enable_write(0);
        return false;
    }

    disp0_dma_enable_write(0);
    return true;
}

static bool ws2812_show(uint32_t timeout)
{
    if (!ws2812_load_framebuffer()) {
        return false;
    }

    disp0_init_write(1);
    disp0_init_write(0);

    if (!wait_until_ws2812_busy_starts(timeout)) {
        return false;
    }

    return wait_until_ws2812_done(timeout);
}

static void uart_write_byte(uint8_t value)
{
    while (uart_txfull_read()) {
    }
    uart_rxtx_write(value);
}

static bool uart_read_byte(uint8_t *value)
{
    if (uart_rxempty_read()) {
        return false;
    }
    *value = (uint8_t)uart_rxtx_read();
    uart_ev_pending_write(2);
    return true;
}

static uint16_t crc16_update(uint16_t crc, uint8_t value)
{
    uint8_t i;

    crc ^= (uint16_t)value << 8;
    for (i = 0; i < 8u; i++) {
        if (crc & 0x8000u) {
            crc = (uint16_t)((crc << 1) ^ 0x1021u);
        } else {
            crc = (uint16_t)(crc << 1);
        }
    }

    return crc;
}

static void write_u16_le(uint16_t value)
{
    uart_write_byte((uint8_t)(value & 0xffu));
    uart_write_byte((uint8_t)(value >> 8));
}

static void send_packet(uint8_t command, uint16_t sequence, const uint8_t *payload, uint16_t length)
{
    uint16_t crc = 0xffffu;
    uint16_t i;

    uart_write_byte(PROTO_SOF0);
    uart_write_byte(PROTO_SOF1);

    uart_write_byte(PROTO_VERSION);
    crc = crc16_update(crc, PROTO_VERSION);
    uart_write_byte(command);
    crc = crc16_update(crc, command);
    uart_write_byte((uint8_t)(sequence & 0xffu));
    crc = crc16_update(crc, (uint8_t)(sequence & 0xffu));
    uart_write_byte((uint8_t)(sequence >> 8));
    crc = crc16_update(crc, (uint8_t)(sequence >> 8));
    uart_write_byte((uint8_t)(length & 0xffu));
    crc = crc16_update(crc, (uint8_t)(length & 0xffu));
    uart_write_byte((uint8_t)(length >> 8));
    crc = crc16_update(crc, (uint8_t)(length >> 8));

    for (i = 0; i < length; i++) {
        uart_write_byte(payload[i]);
        crc = crc16_update(crc, payload[i]);
    }

    write_u16_le(crc);
}

static void send_status(uint8_t response_command, uint16_t sequence, uint8_t original_command,
    uint8_t status, const char *message)
{
    uint8_t payload[50];
    uint16_t i = 0;

    payload[i++] = original_command;
    payload[i++] = status;
    while ((message != 0) && (*message != 0) && (i < sizeof(payload))) {
        payload[i++] = (uint8_t)*message++;
    }

    send_packet(response_command, sequence, payload, i);
}

static void send_ack(uint16_t sequence, uint8_t original_command, const char *message)
{
    send_status(CMD_ACK, sequence, original_command, STATUS_OK, message);
}

static void send_nack(uint16_t sequence, uint8_t original_command, uint8_t status, const char *message)
{
    send_status(CMD_NACK, sequence, original_command, status, message);
}

static void handle_set_frame(void)
{
    uint16_t i;

    if (rx_length != WS2812_FRAME_BYTES) {
        send_nack(rx_sequence, rx_command, STATUS_INVALID_LENGTH, "frame length");
        return;
    }

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        uint8_t r = rx_payload[i * 3u + 0u];
        uint8_t g = rx_payload[i * 3u + 1u];
        uint8_t b = rx_payload[i * 3u + 2u];
        ws2812_set_pixel(i, r, g, b);
    }

    if (!ws2812_show(WS2812_SHOW_TIMEOUT)) {
        send_nack(rx_sequence, rx_command, STATUS_WS2812_TIMEOUT, "show timeout");
        return;
    }

    send_ack(rx_sequence, rx_command, "frame shown");
}

static void handle_packet(void)
{
    static const uint8_t info[] =
        "WS2812 Studio FW 0.1|Colorlight 5A-75B V8.2|8x8|64|GRB|DMA|115200";

    switch (rx_command) {
    case CMD_PING:
        send_ack(rx_sequence, rx_command, "pong");
        break;
    case CMD_GET_INFO:
    {
        uint8_t payload[2 + sizeof(info) - 1];
        uint16_t i;
        payload[0] = CMD_GET_INFO;
        payload[1] = STATUS_OK;
        for (i = 0; i < (sizeof(info) - 1u); i++) {
            payload[2u + i] = info[i];
        }
        send_packet(CMD_ACK, rx_sequence, payload, sizeof(payload));
        break;
    }
    case CMD_SET_FRAME:
        handle_set_frame();
        break;
    case CMD_CLEAR:
        if (rx_length != 0u) {
            send_nack(rx_sequence, rx_command, STATUS_INVALID_LENGTH, "clear length");
            break;
        }
        ws2812_fill(0, 0, 0);
        (void)ws2812_show(WS2812_SHOW_TIMEOUT);
        send_ack(rx_sequence, rx_command, "cleared");
        break;
    case CMD_SET_BRIGHTNESS:
        if (rx_length != 1u) {
            send_nack(rx_sequence, rx_command, STATUS_INVALID_LENGTH, "brightness length");
            break;
        }
        brightness = rx_payload[0];
        (void)brightness;
        send_ack(rx_sequence, rx_command, "brightness stored");
        break;
    case CMD_STOP:
        send_ack(rx_sequence, rx_command, "stopped");
        break;
    default:
        send_nack(rx_sequence, rx_command, STATUS_UNKNOWN_COMMAND, "unknown command");
        break;
    }
}

static void parser_reset(void)
{
    parser_state = WAIT_SOF_1;
    parser_crc = 0xffffu;
    rx_index = 0u;
    rx_length = 0u;
}

static void parser_poll_byte(uint8_t byte)
{
    switch (parser_state) {
    case WAIT_SOF_1:
        if (byte == PROTO_SOF0) {
            parser_state = WAIT_SOF_2;
        }
        break;
    case WAIT_SOF_2:
        parser_state = (byte == PROTO_SOF1) ? READ_VERSION : WAIT_SOF_1;
        break;
    case READ_VERSION:
        if (byte != PROTO_VERSION) {
            parser_reset();
            break;
        }
        parser_crc = crc16_update(0xffffu, byte);
        parser_state = READ_COMMAND;
        break;
    case READ_COMMAND:
        rx_command = byte;
        parser_crc = crc16_update(parser_crc, byte);
        parser_state = READ_SEQUENCE_0;
        break;
    case READ_SEQUENCE_0:
        rx_sequence = byte;
        parser_crc = crc16_update(parser_crc, byte);
        parser_state = READ_SEQUENCE_1;
        break;
    case READ_SEQUENCE_1:
        rx_sequence |= (uint16_t)byte << 8;
        parser_crc = crc16_update(parser_crc, byte);
        parser_state = READ_LENGTH_0;
        break;
    case READ_LENGTH_0:
        rx_length = byte;
        parser_crc = crc16_update(parser_crc, byte);
        parser_state = READ_LENGTH_1;
        break;
    case READ_LENGTH_1:
        rx_length |= (uint16_t)byte << 8;
        parser_crc = crc16_update(parser_crc, byte);
        if (rx_length > PROTO_MAX_PAYLOAD) {
            send_nack(rx_sequence, rx_command, STATUS_INVALID_LENGTH, "payload too large");
            parser_reset();
        } else if (rx_length == 0u) {
            parser_state = READ_CRC_0;
        } else {
            rx_index = 0u;
            parser_state = READ_PAYLOAD;
        }
        break;
    case READ_PAYLOAD:
        rx_payload[rx_index++] = byte;
        parser_crc = crc16_update(parser_crc, byte);
        if (rx_index >= rx_length) {
            parser_state = READ_CRC_0;
        }
        break;
    case READ_CRC_0:
        rx_crc = byte;
        parser_state = READ_CRC_1;
        break;
    case READ_CRC_1:
        rx_crc |= (uint16_t)byte << 8;
        if (rx_crc != parser_crc) {
            send_nack(rx_sequence, rx_command, STATUS_CRC_ERROR, "crc");
        } else {
            handle_packet();
        }
        parser_reset();
        break;
    default:
        parser_reset();
        break;
    }
}

static void uart_protocol_poll(void)
{
    uint8_t byte;

    while (uart_read_byte(&byte)) {
        parser_poll_byte(byte);
    }
}

int main(void)
{
    parser_reset();
    ws2812_fill(0, 0, 0);
    (void)ws2812_show(WS2812_SHOW_TIMEOUT);

    while (1) {
        uart_protocol_poll();
    }

    return 0;
}

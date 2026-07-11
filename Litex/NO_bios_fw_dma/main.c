#include <stdbool.h>
#include <stdint.h>
#include <generated/csr.h>

#define WS2812_HW_LEDS 64u
#define WS2812_SHOW_TIMEOUT 1000000u
#define WS2812_DMA_TIMEOUT  1000000u
#define WS2812_BRIGHTNESS   0x10u

static volatile uint32_t ws2812_buffer[WS2812_HW_LEDS] __attribute__((aligned(4)));

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

static uint32_t ws2812_pack_grb(uint8_t r, uint8_t g, uint8_t b)
{
    return ((uint32_t)g << 16) | ((uint32_t)r << 8) | (uint32_t)b;
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

static void ws2812_set_pixel_grb(uint32_t index, uint8_t r, uint8_t g, uint8_t b)
{
    ws2812_set_pixel_word(index, ws2812_pack_grb(r, g, b));
}

static void ws2812_fill_word(uint32_t word)
{
    uint32_t i;

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        ws2812_set_pixel_word(i, word);
    }
}

static void ws2812_fill(uint8_t r, uint8_t g, uint8_t b)
{
    ws2812_fill_word(ws2812_pack_rgb(r, g, b));
}

static void ws2812_clear(void)
{
    ws2812_fill_word(0);
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

static void pattern_solid_rgb(uint8_t r, uint8_t g, uint8_t b)
{
    ws2812_fill(r, g, b);
    (void)ws2812_show(WS2812_SHOW_TIMEOUT);
}

static void pattern_single_sweep(void)
{
    uint32_t i;

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        ws2812_clear();
        ws2812_set_pixel(i, WS2812_BRIGHTNESS, 0, 0);
        (void)ws2812_show(WS2812_SHOW_TIMEOUT);
        ws2812_delay(2000);
    }
}

static void pattern_rows(void)
{
    uint32_t row;
    uint32_t col;

    for (row = 0; row < 8u; row++) {
        ws2812_clear();
        for (col = 0; col < 8u; col++) {
            ws2812_set_pixel(row * 8u + col, 0, WS2812_BRIGHTNESS, 0);
        }
        (void)ws2812_show(WS2812_SHOW_TIMEOUT);
        ws2812_delay(4000);
    }
}

static void pattern_columns(void)
{
    uint32_t row;
    uint32_t col;

    for (col = 0; col < 8u; col++) {
        ws2812_clear();
        for (row = 0; row < 8u; row++) {
            ws2812_set_pixel(row * 8u + col, 0, 0, WS2812_BRIGHTNESS);
        }
        (void)ws2812_show(WS2812_SHOW_TIMEOUT);
        ws2812_delay(4000);
    }
}

static void pattern_checkerboard(void)
{
    uint32_t i;

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        if ((i + (i / 8u)) & 1u) {
            ws2812_set_pixel(i, WS2812_BRIGHTNESS, 0, 0);
        } else {
            ws2812_set_pixel(i, 0, 0, WS2812_BRIGHTNESS);
        }
    }
    (void)ws2812_show(WS2812_SHOW_TIMEOUT);
}

static void pattern_gradient(uint32_t phase)
{
    uint32_t i;

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        uint8_t r = (uint8_t)((i + phase) & 0x0f);
        uint8_t g = (uint8_t)(((i >> 1) + phase) & 0x0f);
        uint8_t b = (uint8_t)(((i >> 2) + phase) & 0x0f);
        ws2812_set_pixel(i, r, g, b);
    }
    (void)ws2812_show(WS2812_SHOW_TIMEOUT);
}

int main(void)
{
    uint32_t frame = 0;

    while (1) {
        ws2812_clear();
        (void)ws2812_show(WS2812_SHOW_TIMEOUT);
        ws2812_delay(10000);

        pattern_solid_rgb(WS2812_BRIGHTNESS, 0, 0);
        ws2812_delay(10000);

        pattern_solid_rgb(0, WS2812_BRIGHTNESS, 0);
        ws2812_delay(10000);

        pattern_solid_rgb(0, 0, WS2812_BRIGHTNESS);
        ws2812_delay(10000);

        pattern_solid_rgb(WS2812_BRIGHTNESS / 2u,
                          WS2812_BRIGHTNESS / 2u,
                          WS2812_BRIGHTNESS / 2u);
        ws2812_delay(10000);

        pattern_single_sweep();
        pattern_rows();
        pattern_columns();
        pattern_checkerboard();
        ws2812_delay(10000);

        pattern_gradient(frame++);
        ws2812_delay(10000);
    }

    return 0;
}

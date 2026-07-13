#include <stdbool.h>
#include <stdint.h>
#include <generated/csr.h>

#include "generated_animation.h"

#define WS2812_HW_LEDS       64u
#define WS2812_SHOW_TIMEOUT  1000000u
#define WS2812_DMA_TIMEOUT   1000000u
#define WS2812_SYS_CLK_HZ    60000000u

static volatile uint32_t ws2812_buffer[WS2812_HW_LEDS] __attribute__((aligned(4)));

static void ws2812_delay(unsigned int cycles)
{
    volatile unsigned int i;

    for (i = 0; i < cycles; i++) {
        __asm__ volatile("nop");
    }
}

static void delay_ms(uint32_t ms)
{
    uint32_t i;

    for (i = 0; i < ms; i++) {
        ws2812_delay(WS2812_SYS_CLK_HZ / 6000u);
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

static void ws2812_copy_generated_frame(uint32_t frame_index)
{
    uint32_t i;

    for (i = 0; i < WS2812_HW_LEDS; i++) {
        ws2812_buffer[i] = ws2812_animation_frames[frame_index][i] & 0x00ffffffu;
    }
}

static void ws2812_show_generated_frame(uint32_t frame_index)
{
    ws2812_copy_generated_frame(frame_index);
    (void)ws2812_show(WS2812_SHOW_TIMEOUT);
}

int main(void)
{
    uint32_t frame;

    while (1) {
        for (frame = 0; frame < WS2812_ANIMATION_FRAME_COUNT; frame++) {
            ws2812_show_generated_frame(frame);
            delay_ms(ws2812_frame_durations_ms[frame]);
        }

        if (!WS2812_ANIMATION_LOOP) {
            break;
        }
    }

    while (1) {
    }

    return 0;
}

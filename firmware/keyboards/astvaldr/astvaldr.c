#include "quantum.h"

/* GPIO11 switches the LED supply (VRGB) on the Lemon Wired. On these boards
 * HIGH is on, found by test: rianadon's pinout notes say active low, and his
 * firmware uses low only on a later revision. It is set before the lighting
 * starts, because the LEDs only show data sent while they are powered. */
void keyboard_pre_init_kb(void) {
    gpio_set_pin_output(GP11);
    gpio_write_pin_high(GP11);
    keyboard_pre_init_user();
}

/* A command over raw HID, beside VIA's own (this QMK's VIA no longer handles a
 * bootloader jump itself): "BOOT" jumps to the RP2040 bootloader. Sent by
 * to_bootloader.py, so a half can be flashed without touching it. */
#ifdef VIA_ENABLE
bool via_command_kb(uint8_t *data, uint8_t length) {
    if (length >= 4 && data[0] == 'B' && data[1] == 'O' && data[2] == 'O' && data[3] == 'T') {
        reset_keyboard();
        return true;
    }
    return false;
}
#endif

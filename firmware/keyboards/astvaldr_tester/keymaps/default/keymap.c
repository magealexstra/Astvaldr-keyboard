/* Astvaldr matrix tester: one half, the Lemon Wired v0.4's full 7x7 matrix.
 * Every key is KC_NO, so nothing is typed. Each press is printed to the
 * console as the Lemon's own names: R1 to R7, C1 to C7. */
#include QMK_KEYBOARD_H
#include "print.h"

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO
    ),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    uprintf("KEY R%u C%u %s\n", record->event.key.row + 1, record->event.key.col + 1,
            record->event.pressed ? "down" : "up");
    return true;
}

/* The right half's EC11 on the VIK breakout: A on GP26, B on GP27, push on GP13
 * (a direct pin to ground, outside the matrix). Turns and pushes are printed. */
#define ENC_PUSH_PIN GP13

void keyboard_post_init_user(void) {
    gpio_set_pin_input_high(ENC_PUSH_PIN);
}

bool encoder_update_user(uint8_t index, bool clockwise) {
    uprintf("ENC %u %s\n", index, clockwise ? "cw" : "ccw");
    return false;
}

void housekeeping_task_user(void) {
    static bool     was_down = false;
    static uint32_t last     = 0;
    if (timer_elapsed32(last) < 10) return;
    last      = timer_read32();
    bool down = !gpio_read_pin(ENC_PUSH_PIN);
    if (down != was_down) {
        was_down = down;
        uprintf("PUSH %s\n", down ? "down" : "up");
    }
}

/* Flash mode over USB: a raw HID report starting "BOOT" jumps to the RP2040
 * bootloader (sent by to_bootloader.py), so no button is needed. */
#include "raw_hid.h"

void raw_hid_receive(uint8_t *data, uint8_t length) {
    if (length >= 4 && data[0] == 'B' && data[1] == 'O' && data[2] == 'O' && data[3] == 'T') {
        reset_keyboard();
    }
}

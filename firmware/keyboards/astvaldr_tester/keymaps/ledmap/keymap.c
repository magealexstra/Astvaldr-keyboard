/* Astvaldr LED mapper (a keymap of the matrix tester). Lights LED n alone, in white,
 * starting at 0. Tap the key that LED sits under: the console prints
 * "LED n R<row> C<col>" (the Lemon's own names, 1-based) and moves to the next LED.
 * If no key is pressed within 3 s of an LED lighting (an LED under no key), it prints
 * "LED n NONE" and moves on; a key that is down holds the timer until it is released.
 * The timer first starts about 5 s after boot, once the ready line has printed, so the
 * host has time to open the console. After the last LED it prints "DONE" and lights
 * nothing. Runs on one half at a time; n counts that half's own 48 LEDs. */
#include QMK_KEYBOARD_H
#include "print.h"
#include "raw_hid.h"

#define LED_WHITE 96   /* the main firmware's brightness cap */
#define SKIP_MS 3000   /* no press this long: the LED sits under no key */
#define READY_MS 5000  /* after boot, before the ready line and LED 0's timer */

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

/* Positions do not matter here: every LED is driven by index alone. */
led_config_t g_led_config = {
    {[0 ... MATRIX_ROWS - 1] = {[0 ... MATRIX_COLS - 1] = NO_LED}},
    {[0 ... RGB_MATRIX_LED_COUNT - 1] = {0, 0}},
    {[0 ... RGB_MATRIX_LED_COUNT - 1] = LED_FLAG_KEYLIGHT},
};

static uint8_t  current   = 0;     /* the LED that is lit */
static bool     held      = false; /* a key is down: the skip timer waits for its release */
static keypos_t held_key;
static bool     announced = false; /* the ready line has printed and the timer runs */
static uint16_t lit_since;         /* when the current LED's timer started */

static void advance(void) {
    current++;
    lit_since = timer_read();
    if (current >= RGB_MATRIX_LED_COUNT) uprintf("DONE\n");
}

/* GPIO11 switches the LED supply on the Lemon Wired (HIGH is on), as in astvaldr.c. */
void keyboard_pre_init_user(void) {
    gpio_set_pin_output(GP11);
    gpio_write_pin_high(GP11);
}

void keyboard_post_init_user(void) {
    rgb_matrix_enable_noeeprom();
    rgb_matrix_mode_noeeprom(RGB_MATRIX_SOLID_COLOR);
    rgb_matrix_sethsv_noeeprom(0, 0, 0);
}

/* Prints the ready line once the host has had time to open the console, then starts
 * the skip timer; skips an LED nobody pressed a key for. */
void housekeeping_task_user(void) {
    if (!announced) {
        if (timer_read() < READY_MS) return;
        announced = true;
        uprintf("LEDMAP ready: %u LEDs, LED %u lit, %u s per LED\n", RGB_MATRIX_LED_COUNT, current, SKIP_MS / 1000);
        lit_since = timer_read();
        return;
    }
    if (!held && current < RGB_MATRIX_LED_COUNT && timer_elapsed(lit_since) >= SKIP_MS) {
        uprintf("LED %u NONE\n", current);
        advance();
    }
}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    keypos_t k = record->event.key;
    if (record->event.pressed) {
        if (!held) {
            held     = true;
            held_key = k;
        }
        return false;
    }
    if (!held || k.row != held_key.row || k.col != held_key.col) return false;
    held = false;
    if (current >= RGB_MATRIX_LED_COUNT) {
        uprintf("DONE\n");
        return false;
    }
    uprintf("LED %u R%u C%u\n", current, k.row + 1, k.col + 1);
    advance();
    return false;
}

bool rgb_matrix_indicators_user(void) {
    for (uint8_t i = 0; i < RGB_MATRIX_LED_COUNT; i++) {
        uint8_t v = (i == current) ? LED_WHITE : 0;
        rgb_matrix_set_color(i, v, v, v);
    }
    return false;
}

/* Flash mode over USB: a raw HID report starting "BOOT" jumps to the RP2040
 * bootloader (sent by to_bootloader.py), so no button is needed. */
void raw_hid_receive(uint8_t *data, uint8_t length) {
    if (length >= 4 && data[0] == 'B' && data[1] == 'O' && data[2] == 'O' && data[3] == 'T') {
        reset_keyboard();
    }
}

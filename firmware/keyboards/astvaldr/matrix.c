/* Astvaldr's matrix scan ("lite" custom matrix): one half's 7x7 ROW2COL matrix,
 * plus the EC11's push. The push is a direct pin to ground (GP13, the VIK
 * breakout's CS), outside the matrix; it is read into R7 C7, which no switch
 * uses, so it travels over the split link like any key. The left half has
 * nothing on GP13: its pull-up reads as not pressed. */
#include <string.h>
#include "matrix.h"
#include "gpio.h"
#include "util.h"

#define ENC_PUSH_PIN GP13
#define ENC_PUSH_ROW 6
#define ENC_PUSH_COL 6

static const pin_t row_pins[] = MATRIX_ROW_PINS;
static const pin_t col_pins[] = MATRIX_COL_PINS;

void matrix_init_custom(void) {
    for (uint8_t r = 0; r < ARRAY_SIZE(row_pins); r++) gpio_set_pin_input_high(row_pins[r]);
    for (uint8_t c = 0; c < ARRAY_SIZE(col_pins); c++) gpio_set_pin_input_high(col_pins[c]);
    gpio_set_pin_input_high(ENC_PUSH_PIN);
}

bool matrix_scan_custom(matrix_row_t current_matrix[]) {
    matrix_row_t next[ARRAY_SIZE(row_pins)] = {0};

    for (uint8_t c = 0; c < ARRAY_SIZE(col_pins); c++) {
        gpio_write_pin_low(col_pins[c]);
        gpio_set_pin_output(col_pins[c]);
        matrix_output_select_delay();
        bool any = false;
        for (uint8_t r = 0; r < ARRAY_SIZE(row_pins); r++) {
            if (!gpio_read_pin(row_pins[r])) {
                next[r] |= (matrix_row_t)1 << c;
                any = true;
            }
        }
        gpio_set_pin_input_high(col_pins[c]);
        matrix_output_unselect_delay(c, any);
    }

    if (!gpio_read_pin(ENC_PUSH_PIN)) next[ENC_PUSH_ROW] |= (matrix_row_t)1 << ENC_PUSH_COL;

    bool changed = memcmp(current_matrix, next, sizeof(next)) != 0;
    if (changed) memcpy(current_matrix, next, sizeof(next));
    return changed;
}

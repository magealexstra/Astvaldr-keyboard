#pragma once

/* Handedness is stored on each half at flash time (left.uf2 / right.uf2). */
#define EE_HANDS

/* The link between the halves: the Lemon Wired's "Link Only" USB-C ports,
 * full-duplex serial on GPIO0 and GPIO1 (rianadon's settings for this board). */
#define SPLIT_USB_DETECT
#define SERIAL_USART_FULL_DUPLEX
#define SERIAL_USART_PIN_SWAP
#define SERIAL_USART_TX_PIN GP0
#define SERIAL_USART_RX_PIN GP1

/* The EC11, right half only, on the VIK breakout. A and B are in this order
 * so that a clockwise turn reads clockwise. */
#define ENCODER_A_PINS { }
#define ENCODER_B_PINS { }
#define ENCODER_A_PINS_RIGHT { GP27 }
#define ENCODER_B_PINS_RIGHT { GP26 }

/* Render every LED in one pass. By default QMK splits a frame into passes of
 * about a fifth of the LEDs and draws the layer lighting (keymap.c) after each.
 * Digital Rain repaints every LED on every pass, so later passes wiped the
 * painted keys. Equal to the LED count, QMK's rgb_matrix_get_limits takes its
 * unchunked path (it chunks only when the limit is below the count). */
#define RGB_MATRIX_LED_PROCESS_LIMIT RGB_MATRIX_LED_COUNT

/* Double-tap RESET enters the bootloader. */
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET

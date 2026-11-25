#!/usr/bin/env python3
"""Writes Astvaldr's generated QMK files. Every source is a file in this folder:
  - layers.json: the keymap, every layer, keyed by switch name, plus the cursor-follow keys
    and each layer's lighting
  - switches.json: where each switch sits
  - left-matrix.json / right-matrix.json: the Lemon row and column each switch is wired to
  - left-leds.json / right-leds.json: each half's LED chain in order, the switch each LED sits
    under, or null for a pumpkin that holds no switch
Outputs keyboards/astvaldr/keyboard.json, keyboards/astvaldr/keymaps/default/keymap.c
and astvaldr-via.json (the layout file the VIA app loads).
Run it after any change to layers.json, then build and flash.
Usage: gen_astvaldr.py [--all-effects]
  The default build has the 30 lighting effects kept in led-effects.md; --all-effects
  builds in all 50 that QMK has. The effect numbers differ between the two (led-effects.md)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(HERE, "keyboards", "astvaldr")
U = 19.05  # one key unit in mm

# 4D41 is "MA". Not FEED, QMK's placeholder vendor id: the VIA app refuses a layout file that uses it.
VID, PID = "0x4D41", "0x4156"
# Each half's LED chain: 42 on the uncut Pumpkin Patch and 6 on the Pumpkin Vine. The
# pumpkins that hold no switch keep their LED in the chain; they get no key and stay dark.
LEDS_PER_HALF = 48
# Of 255. Measured through a USB meter: solid white at 96 draws 0.428 A, under the 500 mA
# the board asks for. Raindrops at 96 draws about 0.3 A.
MAX_BRIGHTNESS = 96
STEPS = {"val_steps": 8, "hue_steps": 16, "sat_steps": 32, "speed_steps": 32}
DEFAULT_LIGHT = {"animation": "raindrops", "hue": 200, "sat": 223, "val": MAX_BRIGHTNESS, "speed": 95}
ENC_PUSH = (7, 7)  # the EC11's push, read from GP13 into the right half's spare R7 C7
ENCODER = ("KC_VOLD", "KC_VOLU", "KC_MUTE")  # turn left, turn right, push: the same on every layer
# The pause between a cursor-follow key's shortcut and KDE's Move Mouse to Focus, so KWin
# has moved the focus before the pointer is sent after it. Tune it on the board.
CURSOR_FOLLOW_DELAY_MS = 75

# Every RGB matrix effect QMK has, in its own order (the Effect +/- order). led-effects.md
# numbers them; its Keep column is KEEP below.
ALL_EFFECTS = [
    "solid_color", "alphas_mods", "gradient_up_down", "gradient_left_right", "breathing",
    "band_sat", "band_val", "band_pinwheel_sat", "band_pinwheel_val", "band_spiral_sat", "band_spiral_val",
    "cycle_all", "cycle_left_right", "cycle_up_down", "rainbow_moving_chevron", "cycle_out_in",
    "cycle_out_in_dual", "cycle_pinwheel", "cycle_spiral", "dual_beacon", "rainbow_beacon",
    "rainbow_pinwheels", "flower_blooming", "raindrops", "jellybean_raindrops", "hue_breathing",
    "hue_pendulum", "hue_wave", "pixel_rain", "pixel_flow", "pixel_fractal", "typing_heatmap",
    "digital_rain", "solid_reactive_simple", "solid_reactive", "solid_reactive_wide",
    "solid_reactive_multiwide", "solid_reactive_cross", "solid_reactive_multicross",
    "solid_reactive_nexus", "solid_reactive_multinexus", "splash", "multisplash", "solid_splash",
    "solid_multisplash", "starlight_smooth", "starlight", "starlight_dual_sat", "starlight_dual_hue",
    "riverflow",
]
KEEP = [1, 2] + list(range(5, 12)) + [24, 29, 30] + list(range(32, 42)) + list(range(43, 51))
assert len(ALL_EFFECTS) == 50 and len(KEEP) == 30
ALL = "--all-effects" in sys.argv
EFFECTS = ALL_EFFECTS if ALL else [ALL_EFFECTS[n - 1] for n in KEEP]

pos = json.load(open(os.path.join(HERE, "switches.json")))["switches"]
source = json.load(open(os.path.join(HERE, "layers.json")))
keymap_layers = source["layers"]
wired = {}
for half in ("left", "right"):
    wired.update(json.load(open(os.path.join(HERE, f"{half}-matrix.json")))["switches"])
assert set(wired) == set(pos), "the matrix maps and switches.json name different switches"

FINGER = ["xpi", "pi", "ri", "mi", "po", "xpo", "xpo1"]  # outer pinky to inner index


def row_ids(side, level):
    cols = [c for c in FINGER if f"{side}_{c}_{level}" in pos]
    return [f"{side}_{c}_{level}" for c in (cols if side == "L" else reversed(cols))]


def thumb_ids(side, row):
    order = ["-1", "0", "+1"] if side == "L" else ["+1", "0", "-1"]
    return [f"{side}_{row}_{n}" for n in order]


# The LAYOUT order, as the board is seen from above: each row left half then right half.
rows = [row_ids("L", lv) + row_ids("R", lv) for lv in ("+3", "+2", "+1", "0", "-1", "-2")]
rows += [thumb_ids("L", "pri") + thumb_ids("R", "pri"), thumb_ids("L", "pri-1") + thumb_ids("R", "pri-1")]
order = [k for r in rows for k in r]
assert sorted(order) == sorted(pos), "the layout order misses or repeats a switch"


def matrix_of(sw):
    r, c = wired[sw]["row"], wired[sw]["col"]
    return [r - 1 + (7 if sw.startswith("R_") else 0), c - 1]


ENC_MATRIX = [ENC_PUSH[0] - 1 + 7, ENC_PUSH[1] - 1]
used = [tuple(matrix_of(k)) for k in order]
assert len(set(used)) == len(used) and tuple(ENC_MATRIX) not in used

# ---- keyboard.json -------------------------------------------------------
top = max(s["y"] for s in pos.values())
left_min = min(s["x"] for s in pos.values() if s["side"] == "left")
left_max = max(s["x"] for s in pos.values() if s["side"] == "left")
right_min = min(s["x"] for s in pos.values() if s["side"] == "right")
right_off = (left_max - left_min) / U + 3


def xy(sw):
    s = pos[sw]
    x = (s["x"] - left_min) / U if s["side"] == "left" else (s["x"] - right_min) / U + right_off
    return round(x, 2), round((top - s["y"]) / U, 2)


layout = []
for k in order:
    x, y = xy(k)
    layout.append({"label": k, "matrix": matrix_of(k), "x": x, "y": y})
layout.append({"label": "EC11 push", "matrix": ENC_MATRIX, "x": right_off + 3, "y": 0, "encoder": 0})

# Per-key lighting: every LED in chain order (left half, then right), placed where its key
# sits, on QMK's 224 x 64 lighting grid. A spare takes its neighbour's place and no flags,
# which keeps it dark. LED_OF is each switch's index in that order, for the layer lighting.
max_x = max(k["x"] for k in layout)
max_y = max(k["y"] for k in layout)
led_layout = []
LED_OF = {}
for half in ("left", "right"):
    chain = json.load(open(os.path.join(HERE, f"{half}-leds.json")))["leds"][:LEDS_PER_HALF]
    assert sorted(c for c in chain if c) == sorted(k for k in order if k.startswith(half[0].upper())), half
    last = None
    for sw in chain:
        ref = sw or last or next(c for c in chain if c)
        x, y = xy(ref)
        led = {"x": round(x / max_x * 224), "y": round(y / max_y * 64), "flags": 4 if sw else 0}
        if sw:
            led["matrix"] = matrix_of(sw)
            LED_OF[sw] = len(led_layout)
            last = sw
        led_layout.append(led)

keyboard = {
    "keyboard_name": "Astvaldr",
    "manufacturer": "Mage",
    "maintainer": "mage",
    "usb": {"vid": VID, "pid": PID, "device_version": "0.1.0"},
    "processor": "RP2040",
    "bootloader": "rp2040",
    "matrix_pins": {
        "rows": ["GP3", "GP4", "GP5", "GP6", "GP7", "GP8", "GP9"],
        "cols": ["GP25", "GP24", "GP23", "GP22", "GP21", "GP20", "GP10"],
    },
    "diode_direction": "ROW2COL",
    "features": {"extrakey": True, "mousekey": True, "encoder": True, "rgb_matrix": True},
    "dynamic_keymap": {"layer_count": len(keymap_layers)},
    "split": {
        "enabled": True,
        "serial": {"driver": "vendor"},
        # Each half knows the other's keys and the layer, for effects that follow them and for
        # the layer lighting. The lighting settings (effect, colors) reach the other half on
        # their own: QMK sends them over whenever they change on the half that is plugged in.
        "transport": {"sync": {"matrix_state": True, "layer_state": True}},
    },
    "ws2812": {"pin": "GP2", "driver": "vendor"},
    "rgb_matrix": {
        "driver": "ws2812",
        "split_count": [LEDS_PER_HALF, LEDS_PER_HALF],
        "max_brightness": MAX_BRIGHTNESS,
        **STEPS,
        "default": DEFAULT_LIGHT,
        "sleep": True,
        "animations": {name: True for name in EFFECTS},
        "layout": led_layout,
    },
    "layouts": {"LAYOUT": {"layout": layout}},
}
json.dump(keyboard, open(os.path.join(KB, "keyboard.json"), "w"), indent=4)

# ---- keymap.c ------------------------------------------------------------
follow = source["cursor_follow"]
CUSTOM = list(follow["keys"])  # custom keycodes, QK_KB_0 onward (VIA shows them by name)
assert len(CUSTOM) <= 32
for n, spec in enumerate(keymap_layers):
    assert set(spec["bindings"]) == set(pos), f"layer {n} must name every switch, and only real ones (KC_NO for a key that does nothing)"
    assert "_______" not in spec["bindings"].values(), f"layer {n} has a fall-through key"


def layer(keys):
    lines = ["        " + ", ".join(keys[k] for k in r) + "," for r in rows]
    return "\n".join(lines) + f"\n        {ENCODER[2]}"


blocks = [f"    [{n}] = LAYOUT(\n{layer(spec['bindings'])}\n    )," for n, spec in enumerate(keymap_layers)]
notes = [f" *   {n}: {spec['name']}" for n, spec in enumerate(keymap_layers)]
enc = [f"    [{n}] = {{ENCODER_CCW_CW({ENCODER[0]}, {ENCODER[1]})}}," for n in range(len(keymap_layers))]

# Cursor follow: tap the shortcut, wait, tap the follow-up. Nothing else is kept between presses.
cf_enum = ",\n".join(f"    {k}" + (" = QK_KB_0" if i == 0 else "") for i, k in enumerate(CUSTOM))
cf_cases = "\n".join(f"        case {k}:\n            shortcut = {follow['keys'][k]};\n            break;" for k in CUSTOM)

# Layer lighting
colors = source["colors"]
effect_layers, paints = {}, {}
for n, spec in enumerate(keymap_layers):
    light = spec.get("lighting", {})
    if "effect" in light:
        assert light["effect"] in EFFECTS, f"layer {n}'s effect {light['effect']} is not in this build"
        effect_layers[n] = light["effect"]
    entries = []
    for p in light.get("paint", []):
        keys = p["keys"]
        if keys == "working":
            keys = [k for k in order if spec["bindings"][k] != "KC_NO"]
        elif keys == "dead":
            keys = [k for k in order if spec["bindings"][k] == "KC_NO"]
        assert set(keys) <= set(pos), f"layer {n} paints a switch the board does not have"
        hs = colors[p["color"]]
        for k in keys:
            entries.append((LED_OF[k], hs, k, p["color"]))
    if entries:
        paints[n] = entries


def paint_row(led, hs, sw, color):
    if hs is None:
        return f"    {{{led}, 0, 0, true}}, /* {sw}: {color} */"
    return f"    {{{led}, {hs[0]}, {hs[1]}, false}}, /* {sw}: {color} */"


paint_tables = "\n".join(
    f"static const paint_t paint_layer_{n}[] = {{\n" + "\n".join(paint_row(*e) for e in entries) + "\n};\n"
    for n, entries in paints.items()
)
paint_cases = "\n".join(
    f"        case {n}:\n            table = paint_layer_{n};\n            count = ARRAY_SIZE(paint_layer_{n});\n            break;"
    for n in paints
)
enter = "\n".join(
    f"    if (layer_state_cmp(state, {n}) && !layer_state_cmp(layer_state, {n})) {{\n"
    f"        rgb_matrix_mode_noeeprom(RGB_MATRIX_{eff.upper()});\n    }}"
    for n, eff in effect_layers.items()
)
leave = " || ".join(f"(layer_state_cmp(layer_state, {n}) && !layer_state_cmp(state, {n}))" for n in effect_layers)
if len(effect_layers) > 1:  # another effect layer still on keeps its effect
    leave = f"({leave}) && !(" + " || ".join(f"layer_state_cmp(state, {n})" for n in effect_layers) + ")"

lighting_c = f"""
/* Layer lighting, from each layer's "lighting" in layers.json. */
typedef struct {{
    uint8_t led;
    uint8_t hue;
    uint8_t sat;
    bool    dark;
}} paint_t;

{paint_tables}
/* The running effect draws first; then the keys of the highest layer that is on are painted
 * over it, at the current brightness, so they stay under the brightness cap. Both halves run
 * this, each for its own LEDs, from the layer state the halves share. */
bool rgb_matrix_indicators_advanced_user(uint8_t led_min, uint8_t led_max) {{
    const paint_t *table = NULL;
    uint8_t        count = 0;
    switch (get_highest_layer(layer_state | default_layer_state)) {{
{paint_cases}
        default:
            return false;
    }}
    uint8_t val = rgb_matrix_get_val();
    for (uint8_t i = 0; i < count; i++) {{
        rgb_t c = table[i].dark ? (rgb_t){{0, 0, 0}} : hsv_to_rgb((hsv_t){{table[i].hue, table[i].sat, val}});
        RGB_MATRIX_INDICATOR_SET_COLOR(table[i].led, c.r, c.g, c.b);
    }}
    return false;
}}
"""
if effect_layers:
    lighting_c += f"""
/* A layer with its own effect switches to it on entry, without saving it. Leaving puts back
 * the effect saved in EEPROM (only the effect: colors and brightness are left as they are).
 * Only the half that is plugged in runs this; QMK sends the effect to the other half. */
layer_state_t layer_state_set_user(layer_state_t state) {{
{enter}
    if ({leave}) {{
        rgb_config_t saved;
        eeconfig_read_rgb_matrix(&saved);
        rgb_matrix_mode_noeeprom(saved.mode);
    }}
    return state;
}}
"""

keymap = (
    "/* Astvaldr. GENERATED by gen_astvaldr.py from layers.json: edit the layers there,\n"
    " * then run the generator, not this file.\n"
    + "\n".join(notes)
    + "\n * The last key of each layer is the EC11's push. */\n"
    "#include QMK_KEYBOARD_H\n"
    '#include "eeconfig.h"\n\n'
    "/* Cursor follow: each of these keys taps its shortcut, waits this long, then taps\n"
    " * CURSOR_FOLLOW_THEN (KDE's Move Mouse to Focus), so the pointer follows the window. */\n"
    f"#define CURSOR_FOLLOW_DELAY_MS {CURSOR_FOLLOW_DELAY_MS}\n"
    f"#define CURSOR_FOLLOW_THEN {follow['then']}\n\n"
    f"enum custom_keycodes {{\n{cf_enum}\n}};\n\n"
    "const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {\n"
    + "\n".join(blocks)
    + "\n};\n\n"
    "const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {\n"
    + "\n".join(enc)
    + "\n};\n\n"
    "bool process_record_user(uint16_t keycode, keyrecord_t *record) {\n"
    "    uint16_t shortcut = KC_NO;\n"
    "    switch (keycode) {\n"
    f"{cf_cases}\n"
    "        default:\n"
    "            return true;\n"
    "    }\n"
    "    if (record->event.pressed) {\n"
    "        tap_code16(shortcut);\n"
    "        wait_ms(CURSOR_FOLLOW_DELAY_MS);\n"
    "        tap_code16(CURSOR_FOLLOW_THEN);\n"
    "    }\n"
    "    return false;\n"
    "}\n"
    + lighting_c
)
os.makedirs(os.path.join(KB, "keymaps", "default"), exist_ok=True)
open(os.path.join(KB, "keymaps", "default", "keymap.c"), "w").write(keymap)

# ---- the VIA app's layout file -------------------------------------------
# A plain grid, not the real stagger: VIA only needs each key to be findable.
cells = []  # (x, y, label)
for y, lv in enumerate(("+3", "+2", "+1", "0", "-1", "-2")):
    for sw in row_ids("L", lv) + row_ids("R", lv):
        col = FINGER.index(sw.split("_")[1])
        x = col if sw.startswith("L_") else 15 - col
        cells.append((x, y, sw))
for y, row in ((6.25, "pri"), (7.25, "pri-1")):
    for i, sw in enumerate(thumb_ids("L", row)):
        cells.append((4.5 + i, y, sw))
    for i, sw in enumerate(thumb_ids("R", row)):
        cells.append((8.5 + i, y, sw))

kle, cur_y = [], 0
for y in sorted({c[1] for c in cells}):
    row, cur_x = [], 0
    for x, _, sw in sorted(c for c in cells if c[1] == y):
        props = {}
        if x != cur_x:
            props["x"] = x - cur_x
        if not row and y != cur_y:
            props["y"] = y - cur_y
        if props:
            row.append(props)
        m = matrix_of(sw)
        row.append(f"{m[0]},{m[1]}")
        cur_x = x + 1
    if y == 6.25:  # the encoder sits beside the right thumbs
        row.append({"x": 12.5 - cur_x})
        row.append(f"{ENC_MATRIX[0]},{ENC_MATRIX[1]}\n\n\n\n\n\n\n\n\ne0")
    kle.append(row)
    cur_y = y + 1


def custom_name(k):
    return k[3:].replace("_", " ").title().replace("Screen", "Window to screen")


via = {
    "name": "Astvaldr",
    "vendorId": VID,
    "productId": PID,
    "matrix": {"rows": 14, "cols": 7},
    "menus": ["qmk_rgb_matrix"],
    # VIA shows the cursor-follow keys (QK_KB_0 onward, in this order) by these names
    "customKeycodes": [
        {"name": custom_name(k), "title": f"{custom_name(k)}, then move the pointer to it", "shortName": custom_name(k)}
        for k in CUSTOM
    ],
    "layouts": {"keymap": kle},
}
json.dump(via, open(os.path.join(HERE, "astvaldr-via.json"), "w"), indent=2)
print(f"wrote keyboard.json ({len(layout)} keys, {len(EFFECTS)} effects), keymap.c "
      f"({len(keymap_layers)} layers), astvaldr-via.json")

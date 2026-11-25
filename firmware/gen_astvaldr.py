#!/usr/bin/env python3
"""Writes Astvaldr's generated QMK files. Every source is a file in this folder:
  - layers.json: the keymap, every layer, keyed by switch name
  - switches.json: where each switch sits
  - left-matrix.json / right-matrix.json: the Lemon row and column each switch is wired to
  - left-leds.json / right-leds.json: each half's LED chain in order, the switch each LED sits
    under, or null for a pumpkin that holds no switch
Outputs keyboards/astvaldr/keyboard.json, keyboards/astvaldr/keymaps/default/keymap.c
and astvaldr-via.json (the layout file the VIA app loads).
Run it after any change to layers.json, then build and flash."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(HERE, "keyboards", "astvaldr")
U = 19.05  # one key unit in mm

# 4D41 is "MA". Not FEED, QMK's placeholder vendor id: the VIA app refuses a layout file that uses it.
VID, PID = "0x4D41", "0x4156"
# Each half's LED chain: 42 on the uncut Pumpkin Patch and 6 on the Pumpkin Vine. The
# pumpkins that hold no switch keep their LED in the chain; they get no key and stay dark.
LEDS_PER_HALF = 48
MAX_BRIGHTNESS = 40  # of 255: 88 LEDs at full white would far exceed a USB port
ENC_PUSH = (7, 7)  # the EC11's push, read from GP13 into the right half's spare R7 C7

pos = json.load(open(os.path.join(HERE, "switches.json")))["switches"]
keymap_layers = json.load(open(os.path.join(HERE, "layers.json")))["layers"]
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
# which keeps it dark.
ANIMATIONS = [
    "solid_color", "breathing", "gradient_up_down", "gradient_left_right", "hue_wave",
    "cycle_all", "cycle_left_right", "cycle_up_down", "cycle_out_in", "cycle_pinwheel", "cycle_spiral",
    "rainbow_moving_chevron", "raindrops",
    "solid_reactive_simple", "solid_reactive", "solid_reactive_multiwide",
    "splash", "multisplash", "solid_splash",
]
max_x = max(k["x"] for k in layout)
max_y = max(k["y"] for k in layout)
led_layout = []
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
    "split": {
        "enabled": True,
        "serial": {"driver": "vendor"},
        # each half knows the other's keys and the layer, for effects that follow them
        "transport": {"sync": {"matrix_state": True, "layer_state": True}},
    },
    "ws2812": {"pin": "GP2", "driver": "vendor"},
    "rgb_matrix": {
        "driver": "ws2812",
        "split_count": [LEDS_PER_HALF, LEDS_PER_HALF],
        "max_brightness": MAX_BRIGHTNESS,
        "sleep": True,
        "animations": {name: True for name in ANIMATIONS},
        "layout": led_layout,
    },
    "layouts": {"LAYOUT": {"layout": layout}},
}
json.dump(keyboard, open(os.path.join(KB, "keyboard.json"), "w"), indent=4)

# ---- keymap.c ------------------------------------------------------------


for spec in keymap_layers:
    assert set(spec["bindings"]) <= set(pos), f"layer '{spec['name']}' names a switch the board does not have"
base = keymap_layers[0]["bindings"]
assert set(base) == set(pos), "the base layer must name every switch (KC_NO for a key that does nothing)"


def code(sw):
    return base[sw]


def layer(fn, last):
    lines = ["        " + ", ".join(fn(k) for k in r) + "," for r in rows]
    return "\n".join(lines) + f"\n        {last}"


uppers = [spec["bindings"] for spec in keymap_layers[1:]]
blocks = [f"    [0] = LAYOUT(\n{layer(code, 'KC_MUTE')}\n    ),"]
notes = [f" *   0: {keymap_layers[0]['name']}"]
for n, (spec, keys) in enumerate(zip(keymap_layers[1:], uppers), start=1):
    blocks.append(f"    [{n}] = LAYOUT(\n{layer(lambda k, keys=keys: keys.get(k, '_______'), '_______')}\n    ),")
    notes.append(f" *   {n}: {spec['name']}")
enc = ["    [0] = {ENCODER_CCW_CW(KC_VOLD, KC_VOLU)},"] + [f"    [{n}] = {{ENCODER_CCW_CW(_______, _______)}}," for n in range(1, len(uppers) + 1)]

keymap = (
    "/* Astvaldr. GENERATED by gen_astvaldr.py from layers.json: edit the layers there,\n"
    " * then run the generator, not this file.\n"
    + "\n".join(notes)
    + "\n * The last key of each layer is the EC11's push. */\n"
    "#include QMK_KEYBOARD_H\n\n"
    "const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {\n"
    + "\n".join(blocks)
    + "\n};\n\n"
    "const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {\n"
    + "\n".join(enc)
    + "\n};\n"
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

via = {
    "name": "Astvaldr",
    "vendorId": VID,
    "productId": PID,
    "matrix": {"rows": 14, "cols": 7},
    "menus": ["qmk_rgb_matrix"],
    "layouts": {"keymap": kle},
}
json.dump(via, open(os.path.join(HERE, "astvaldr-via.json"), "w"), indent=2)
print(f"wrote keyboard.json ({len(layout)} keys), keymap.c, astvaldr-via.json")

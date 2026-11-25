#!/usr/bin/env python3
"""Draws a picture of each of Astvaldr's layers, in the style of QMK Configurator's
print view: a dark panel per layer, a key cap where each switch sits, its legend on it.
Reads layers.json (the keymap) and switches.json (where the keys sit).
Writes into pictures/: astvaldr-layer-<n>.svg and .png, and astvaldr-layers.svg and
.png with every layer on one sheet. Run it with the venv's python (it needs cairosvg
for the .png files): .venv/bin/python render_layers.py"""
import json
import math
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pictures")
U_MM = 19.05
PX = 58  # one key unit in pixels
GAP = 5  # between key caps
PAD = 26  # panel padding
TITLE_H = 54
HALF_GAP_U = 3.0  # space drawn between the halves

PAGE, PANEL, KEY, KEY_EDGE, TEXT, DIM, TITLE = "#262626", "#3d3d3d", "#4a4a4a", "#5c5c5c", "#f0f0f0", "#8a8a8a", "#ffffff"

# A legend is one line, or two lines split by "\n" (for a symbol key: shifted over plain).
NAMED = {
    "KC_NO": "", "_______": "▽",
    "KC_LSFT": "Left\nShift", "KC_RSFT": "Right\nShift", "KC_LCTL": "Left\nCtrl", "KC_RCTL": "Right\nCtrl",
    "KC_LALT": "Left\nAlt", "KC_RALT": "Right\nAlt", "KC_LGUI": "Left\nOS", "KC_RGUI": "Right\nOS",
    "KC_SPC": "Space", "KC_ENT": "Enter", "KC_ESC": "Esc", "KC_TAB": "Tab", "KC_BSPC": "Back\nSpace", "KC_DEL": "Delete",
    "KC_CAPS": "Caps\nLock", "KC_NUM": "Num\nLock", "KC_PSCR": "Print\nScreen", "KC_PAUS": "Pause\nBreak", "KC_INS": "Insert",
    "KC_HOME": "Home", "KC_END": "End", "KC_PGUP": "Page\nUp", "KC_PGDN": "Page\nDown",
    "KC_UP": "Up", "KC_DOWN": "Down", "KC_LEFT": "Left", "KC_RGHT": "Right",
    "KC_COPY": "Copy", "KC_PSTE": "Paste", "KC_CUT": "Cut", "KC_UNDO": "Undo", "KC_STOP": "Stop",
    "KC_MPLY": "Play", "KC_MPRV": "Previous", "KC_MNXT": "Next", "KC_MSTP": "Media\nStop", "KC_MUTE": "Mute",
    "KC_VOLU": "Vol +", "KC_VOLD": "Vol −", "KC_WREF": "Browser\nRefresh",
    "UG_TOGG": "LED\nOn/Off", "UG_NEXT": "LED\nEffect +", "UG_PREV": "LED\nEffect −",
    "UG_VALU": "LED\nBright +", "UG_VALD": "LED\nBright −", "UG_HUEU": "LED\nHue +", "UG_HUED": "LED\nHue −",
    "UG_SATU": "LED\nSat +", "UG_SATD": "LED\nSat −", "UG_SPDU": "LED\nSpeed +", "UG_SPDD": "LED\nSpeed −",
    "QK_BOOT": "Boot\nloader", "C(KC_BSPC)": "Delete\nWord",
}
PAIRS = {  # plain key: (shifted, plain)
    "KC_GRV": "~\n`", "KC_MINS": "_\n-", "KC_EQL": "+\n=", "KC_LBRC": "{\n[", "KC_RBRC": "}\n]", "KC_BSLS": "|\n\\",
    "KC_SCLN": ":\n;", "KC_QUOT": "\"\n'", "KC_COMM": "<\n,", "KC_DOT": ">\n.", "KC_SLSH": "?\n/",
    "KC_1": "!\n1", "KC_2": "@\n2", "KC_3": "#\n3", "KC_4": "$\n4", "KC_5": "%\n5",
    "KC_6": "^\n6", "KC_7": "&\n7", "KC_8": "*\n8", "KC_9": "(\n9", "KC_0": ")\n0",
}
SHIFTED = {
    "KC_EXLM": "!", "KC_AT": "@", "KC_HASH": "#", "KC_DLR": "$", "KC_PERC": "%", "KC_CIRC": "^", "KC_AMPR": "&",
    "KC_ASTR": "*", "KC_LPRN": "(", "KC_RPRN": ")", "KC_UNDS": "_", "KC_PLUS": "+", "KC_PIPE": "|", "KC_DQUO": "\"",
    "KC_COLN": ":", "KC_QUES": "?", "KC_TILD": "~", "KC_LCBR": "{", "KC_RCBR": "}", "KC_LABK": "<", "KC_RABK": ">",
}


def legend(code):
    if code in NAMED:
        return NAMED[code]
    if code in PAIRS:
        return PAIRS[code]
    if code in SHIFTED:
        return SHIFTED[code]
    if code.startswith("KC_F") and code[4:].isdigit():
        return "F" + code[4:]
    if code.startswith("KC_") and len(code) == 4:
        return code[3:]
    if code.startswith("QK_MACRO_"):
        return "Macro\n" + code[9:]
    if code.startswith(("MO(", "TG(", "TO(", "OSL(", "TT(")):
        return code
    return code.replace("KC_", "").replace("_", "\n", 1)


# What the encoder does on each layer (turn, push): set in gen_astvaldr.py, not in layers.json.
ENCODER = [("Vol \u2212 / +", "Mute")]

pos = json.load(open(os.path.join(HERE, "switches.json")))["switches"]
layers = json.load(open(os.path.join(HERE, "layers.json")))["layers"]

top = max(s["y"] for s in pos.values())
left = [s for s in pos.values() if s["side"] == "left"]
right = [s for s in pos.values() if s["side"] == "right"]
left_min, left_max = min(s["x"] for s in left), max(s["x"] for s in left)
right_min, right_max = min(s["x"] for s in right), max(s["x"] for s in right)
right_off = (left_max - left_min) / U_MM + 1 + HALF_GAP_U
cols_u = right_off + (right_max - right_min) / U_MM + 1
rows_u = (top - min(s["y"] for s in pos.values())) / U_MM + 1
PANEL_W, PANEL_H = cols_u * PX + 2 * PAD, rows_u * PX + 2 * PAD
BLOCK_H = TITLE_H + PANEL_H
WIDTH = PANEL_W + 2 * PAD


def key_xy(sw):
    s = pos[sw]
    xu = (s["x"] - left_min) / U_MM if s["side"] == "left" else (s["x"] - right_min) / U_MM + right_off
    return PAD + xu * PX, PAD + (top - s["y"]) / U_MM * PX


def text(x, y, s, size, fill, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="middle" dominant-baseline="central">{escape(s)}</text>')


def thumb_angle(sw):
    """The thumb keys sit along a diagonal: each is turned to face along its row."""
    if "_pri" not in sw:
        return 0
    side, row, _ = sw.split("_")
    (x0, y0), (x1, y1) = key_xy(f"{side}_{row}_-1"), key_xy(f"{side}_{row}_+1")
    a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    return a if side == "L" else a - 180


def cap(x, y, label, angle=0):
    size = PX - GAP
    cx, cy = x + size / 2, y + size / 2
    turn = f' transform="rotate({angle:.1f} {cx:.1f} {cy:.1f})"' if angle else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="6" fill="{KEY}" stroke="{KEY_EDGE}"{turn}/>']
    lines = label.split("\n")
    longest = max(len(line) for line in lines)
    fs = 17 if longest <= 2 else 15 if longest == 3 and len(lines) == 1 else 10.5 if longest <= 8 else 9
    fill = DIM if label == "▽" else TEXT
    if len(lines) == 1:
        out.append(text(cx, cy, lines[0], fs, fill))
    else:
        step = fs * 1.15
        out.append(text(cx, cy - step / 2, lines[0], fs, fill))
        out.append(text(cx, cy + step / 2, lines[1], fs, fill))
    return "".join(out)


def block(n, y0):
    """One layer: its title and its panel, drawn with the panel's top at y0 + TITLE_H."""
    spec = layers[n]
    keys = spec["bindings"]
    g = [text(WIDTH / 2, y0 + TITLE_H / 2, f"Layer {n}: {spec['name']}", 20, TITLE, "bold")]
    py = y0 + TITLE_H
    g.append(f'<rect x="{PAD}" y="{py:.1f}" width="{PANEL_W:.1f}" height="{PANEL_H:.1f}" rx="8" fill="{PANEL}"/>')
    for sw in pos:
        x, y = key_xy(sw)
        g.append(cap(PAD + x, py + y, legend(keys.get(sw, "KC_NO" if n == 0 else "_______")), thumb_angle(sw)))
    # the EC11, drawn between the halves: it is not a switch position
    ex, ey, r = PAD + PANEL_W / 2, py + PAD + PX * 1.1, PX * 0.62
    turn, push = ENCODER[n] if n < len(ENCODER) else ("\u25bd", "\u25bd")
    g.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r:.1f}" fill="{KEY}" stroke="{KEY_EDGE}"/>')
    g.append(text(ex, ey - 9, turn, 10.5, DIM if turn == "\u25bd" else TEXT))
    g.append(text(ex, ey + 9, push, 10.5, DIM if push == "\u25bd" else TEXT))
    g.append(text(ex, ey + r + 14, "encoder: turn, push", 10, DIM))
    return "".join(g)


def sheet(which):
    height = len(which) * BLOCK_H + PAD
    body = "".join(block(n, i * BLOCK_H) for i, n in enumerate(which))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH:.0f}" height="{height:.0f}" '
            f'viewBox="0 0 {WIDTH:.0f} {height:.0f}" font-family="DejaVu Sans, Noto Sans, Arial, sans-serif">'
            f'<rect width="100%" height="100%" fill="{PAGE}"/>{body}</svg>')


os.makedirs(OUT, exist_ok=True)
files = {f"astvaldr-layer-{n}": sheet([n]) for n in range(len(layers))}
files["astvaldr-layers"] = sheet(list(range(len(layers))))
try:
    import cairosvg
except ImportError:
    cairosvg = None
for name, svg in files.items():
    path = os.path.join(OUT, name + ".svg")
    open(path, "w").write(svg)
    if cairosvg:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, name + ".png"), scale=2)
print(f"wrote {len(files)} pictures to {OUT}" + ("" if cairosvg else " (SVG only: cairosvg is not installed)"))

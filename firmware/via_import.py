#!/usr/bin/env python3
"""Copies a keymap saved from the VIA app (its SAVE + LOAD tab) into layers.json, so the
file matches what was arranged on the board. Keys are matched by their wiring
(left-matrix.json, right-matrix.json). VIA's spellings are turned into QMK's.
Layer names in layers.json are kept. Usage: via_import.py <saved.json> [--check]
--check only reports the keys that differ and writes nothing."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = 7
# VIA's name -> QMK's name
NAMES = {"KC_NLCK": "KC_NUM", "KC_PASTE": "KC_PSTE", "KC_WWW_REFRESH": "KC_WREF", "KC_TRNS": "_______"}
NAMES.update({"RGB_TOG": "UG_TOGG", "RGB_MOD": "UG_NEXT", "RGB_RMOD": "UG_PREV", "RGB_VAI": "UG_VALU", "RGB_VAD": "UG_VALD",
              "RGB_HUI": "UG_HUEU", "RGB_HUD": "UG_HUED", "RGB_SAI": "UG_SATU", "RGB_SAD": "UG_SATD",
              "RGB_SPI": "UG_SPDU", "RGB_SPD": "UG_SPDD"})
NAMES.update({f"MACRO({n})": f"QK_MACRO_{n}" for n in range(16)})
SHIFTED = {"1": "EXLM", "2": "AT", "3": "HASH", "4": "DLR", "5": "PERC", "6": "CIRC", "7": "AMPR", "8": "ASTR",
           "9": "LPRN", "0": "RPRN", "MINS": "UNDS", "EQL": "PLUS", "BSLS": "PIPE", "QUOT": "DQUO",
           "SCLN": "COLN", "SLSH": "QUES", "GRV": "TILD", "LBRC": "LCBR", "RBRC": "RCBR", "COMM": "LABK", "DOT": "RABK"}
NAMES.update({f"S(KC_{k})": f"KC_{v}" for k, v in SHIFTED.items()})

saved = json.load(open(sys.argv[1]))
wired = {}
for half in ("left", "right"):
    wired.update(json.load(open(os.path.join(HERE, f"{half}-matrix.json")))["switches"])
index = {(v["row"] - 1 + (7 if k.startswith("R_") else 0)) * COLS + v["col"] - 1: k for k, v in wired.items()}

path = os.path.join(HERE, "layers.json")
doc = json.load(open(path))
new_layers = []
for n, codes in enumerate(saved["layers"]):
    keys = {}
    for i, code in enumerate(codes):
        sw = index.get(i)
        if sw is None:
            continue
        code = NAMES.get(code, code)
        if n == 0:
            keys[sw] = code
        elif code != "_______":
            keys[sw] = code
    if n >= len(doc["layers"]) and not keys:
        continue  # an untouched spare layer
    name = doc["layers"][n]["name"] if n < len(doc["layers"]) else f"Layer {n}"
    new_layers.append({"name": name, "bindings": keys})

changes = []
for n, layer in enumerate(new_layers):
    old = doc["layers"][n]["bindings"] if n < len(doc["layers"]) else {}
    for sw in sorted(set(old) | set(layer["bindings"])):
        a, b = old.get(sw, "_______"), layer["bindings"].get(sw, "_______")
        if a != b:
            changes.append(f"layer {n} {sw}: {a} -> {b}")
print("\n".join(changes) if changes else "no differences")
if "--check" not in sys.argv:
    doc["layers"] = new_layers
    json.dump(doc, open(path, "w"), indent=1)
    print(f"layers.json updated: {len(changes)} keys")

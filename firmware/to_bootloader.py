#!/usr/bin/env python3
"""Puts the Astvaldr half that is plugged into this computer into flash mode
(the RP2040 bootloader, the RPI-RP2 drive) over USB, no button needed.
It writes to the board's raw HID interface (usage page 0xFF60), found by USB
vendor id, a report reading "BOOT". Astvaldr's firmware and the matrix tester
both answer it by jumping to the bootloader.
Looks for Astvaldr (vendor id 4d41) and for the matrix tester and Astvaldr's first
builds (feed).
Usage: to_bootloader.py"""
import glob
import os
import sys
import time

VENDORS = (":00004D41:", ":0000FEED:")


def raw_hid():
    for sysdir in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        try:
            uevent = open(f"{sysdir}/device/uevent").read()
            desc = open(f"{sysdir}/device/report_descriptor", "rb").read(3)
        except OSError:
            continue
        if any(v in uevent for v in VENDORS) and desc == bytes([0x06, 0x60, 0xFF]):
            return "/dev/" + os.path.basename(sysdir)
    return None


dev = raw_hid()
if dev is None:
    sys.exit("no raw HID interface found: the board is not running a firmware that takes the command")
with open(dev, "wb", buffering=0) as f:
    f.write(b"\x00" + b"BOOT".ljust(32, b"\x00"))
time.sleep(1.5)
if raw_hid() is not None:
    sys.exit("sent, but the board is still running its firmware")
print("sent")

#!/usr/bin/env python3
"""Reads a QMK board's console (the raw HID interface on usage page 0xFF31)
straight from /dev/hidraw and appends each line, timestamped, to a log file.
No hidapi library needed. Usage: console_listen.py <logfile> [usb vendor id, default feed]"""
import glob
import os
import sys
import time

log_path = sys.argv[1]
vendor = (sys.argv[2] if len(sys.argv) > 2 else "feed").upper().rjust(8, "0")


def find_console():
    for sysdir in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        try:
            uevent = open(f"{sysdir}/device/uevent").read()
            desc = open(f"{sysdir}/device/report_descriptor", "rb").read(3)
        except OSError:
            continue
        if f":{vendor}:" in uevent and desc == bytes([0x06, 0x31, 0xFF]):
            return "/dev/" + os.path.basename(sysdir)
    return None


with open(log_path, "a", buffering=1) as log:
    while True:
        dev = find_console()
        if dev is None:
            time.sleep(0.5)
            continue
        log.write(f"{time.strftime('%H:%M:%S')} # listening on {dev}\n")
        pending = ""
        try:
            with open(dev, "rb", buffering=0) as f:
                while True:
                    data = f.read(64)
                    if not data:
                        break
                    pending += data.replace(b"\x00", b"").decode("ascii", "replace")
                    while "\n" in pending:
                        line, pending = pending.split("\n", 1)
                        log.write(f"{time.strftime('%H:%M:%S')} {line}\n")
        except OSError:
            pass
        log.write(f"{time.strftime('%H:%M:%S')} # device gone\n")
        time.sleep(0.5)

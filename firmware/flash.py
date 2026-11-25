#!/usr/bin/env python3
"""Flashes a .uf2 onto the Astvaldr half plugged into this computer.
If the half is not already in flash mode (the RPI-RP2 drive), it is sent there
over USB first (to_bootloader.py). Stops with a message at the first step that
fails; nothing is copied unless the RPI-RP2 drive is found and mounted.
Usage: flash.py <firmware.uf2> [--unchecked]
       flash.py --serial   (print the plugged-in half's USB serial and exit)"""

# ---------------------------------------------------------------------------
# EDIT ME: your own boards' serial numbers
#
# Each Lemon's USB serial number, so a half never gets the other half's firmware.
# The two serials below belong to the original builder's boards. If you build your
# own Astvaldr, replace them with yours: plug in one half (running its firmware, not
# in flash mode), run `flash.py --serial`, copy the serial it prints into the line
# for that half, then do the same for the other half.
HALVES = {
    "E6656871D75B702F": "left",
    "E6656871D7198C2F": "right",
}
# ---------------------------------------------------------------------------

import glob
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def plugged_serials():
    """The USB serial of every running Astvaldr (vendor 4d41) or tester (feed) on USB."""
    found = []
    for d in sorted(glob.glob("/sys/bus/usb/devices/*/idVendor")):
        if open(d).read().strip() in ("4d41", "feed"):
            found.append(open(os.path.join(os.path.dirname(d), "serial")).read().strip())
    return found


def plugged_half():
    for serial in plugged_serials():
        return HALVES.get(serial[:16], f"unknown board {serial}")
    return None


# --serial only reads the USB serial from /sys; nothing is flashed or sent to the board.
if "--serial" in sys.argv:
    serials = plugged_serials()
    if not serials:
        sys.exit("no running Astvaldr on USB (vendor 4d41 or feed); a half in flash mode does not show its serial")
    for serial in serials:
        print(f"{serial[:16]}  ({HALVES.get(serial[:16], 'not in HALVES yet')})")
    sys.exit(0)

if len(sys.argv) < 2:
    sys.exit(__doc__)
uf2 = sys.argv[1]
if not os.path.isfile(uf2):
    sys.exit(f"no such file: {uf2}")

# A firmware named *-left.uf2 or *-right.uf2 is only flashed onto that Lemon. A board
# already in flash mode does not show its serial: pass --unchecked to flash it anyway.
want = next((h for h in ("left", "right") if os.path.basename(uf2).endswith(f"-{h}.uf2")), None)


if want and "--unchecked" not in sys.argv:
    have = plugged_half()
    if have is None:
        sys.exit("cannot tell which half is plugged in (no running Astvaldr on USB); pass --unchecked if you are sure")
    if have != want:
        sys.exit(f"refused: {os.path.basename(uf2)} is for the {want} half, and the {have} half is plugged in")


def rp2_partition():
    out = subprocess.run(["lsblk", "-rno", "NAME,LABEL"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == "RPI-RP2":
            return "/dev/" + parts[0]
    return None


def wait_for(fn, seconds):
    end = time.time() + seconds
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(0.5)
    return None


part = rp2_partition()
if part is None:
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "to_bootloader.py")], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"could not send the board to flash mode: {(r.stdout + r.stderr).strip()}")
    part = wait_for(rp2_partition, 10)
    if part is None:
        sys.exit("the board left its firmware but no RPI-RP2 drive appeared")


def mountpoint():
    return subprocess.run(["findmnt", "-rn", "-o", "TARGET", part], capture_output=True, text=True).stdout.strip()


if not mountpoint():
    subprocess.run(["udisksctl", "mount", "-b", part], capture_output=True, text=True)
mnt = wait_for(mountpoint, 5)
if not mnt or not os.path.isfile(os.path.join(mnt, "INFO_UF2.TXT")):
    sys.exit(f"could not mount {part} as the RPI-RP2 drive")

shutil.copy(uf2, mnt)
os.sync()
gone = wait_for(lambda: rp2_partition() is None, 10)
print(f"flashed {os.path.basename(uf2)}" if gone else f"copied {os.path.basename(uf2)}, but the RPI-RP2 drive is still there")

# VIA keeps its own copy of the keymap on the board and only replaces it when the
# firmware's build DATE changes, so a second flash on the same day would leave the old
# keymap in place. Reset it to the firmware's after every flash. This also discards
# any remapping done live in VIA: the keymap on the board is always the built one.
if gone:
    import select

    def raw_hid():
        for s in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
            try:
                if any(v in open(s + "/device/uevent").read() for v in (":00004D41:", ":0000FEED:")) and open(s + "/device/report_descriptor", "rb").read(3) == bytes([6, 0x60, 0xFF]):
                    return "/dev/" + os.path.basename(s)
            except OSError:
                pass
        return None

    dev = wait_for(raw_hid, 10)
    if dev is None:
        sys.exit("flashed, but the board did not come back on USB: the stored keymap was NOT reset")
    time.sleep(1)
    fd = os.open(dev, os.O_RDWR)
    os.write(fd, b"\x00" + bytes([0x06]).ljust(32, b"\x00"))
    if not select.select([fd], [], [], 3)[0]:
        sys.exit("flashed, but the board did not answer the keymap reset")
    print("stored keymap reset to the firmware's")

#!/usr/bin/env python3
"""
carve.py  —  BENIGN reproduction of the "carve payload out of browser cache" step.

Mirrors the malicious one-liner from Appendix C (regex-match between markers,
reassemble the ZIP) but:
  * it EXTRACTS and PRINTS only -- it never executes anything;
  * it works on either a raw asset file or a Chromium Cache_Data directory.

Usage:
    python3 carve.py cached_asset.jpg
    python3 carve.py /path/to/Cache/Cache_Data     # scans f_* / data_* entries

The real attack ran the unzipped binary. Here we stop at "look what was hidden."
"""
import io
import os
import re
import sys
import zipfile

START = b"LABSTART"
END = b"LABEND"


def carve_bytes(blob: bytes):
    m = re.search(re.escape(START) + b"(.*?)" + re.escape(END), blob, re.DOTALL)
    return m.group(1) if m else None


def iter_files(target):
    if os.path.isdir(target):
        for root, _, files in os.walk(target):
            for name in files:
                yield os.path.join(root, name)
    else:
        yield target


def main(target):
    print(f"[carve] scanning: {target}")
    found = 0
    for path in iter_files(target):
        try:
            with open(path, "rb") as f:
                blob = f.read()
        except OSError:
            continue
        payload = carve_bytes(blob)
        if not payload:
            continue
        found += 1
        print(f"[carve] MARKER HIT in {path}  (carved {len(payload)} bytes)")
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as z:
                for entry in z.namelist():
                    print(f"[carve]   zip entry: {entry}")
                    print("[carve]   ---- benign contents ----")
                    print(z.read(entry).decode(errors="replace").rstrip())
                    print("[carve]   --------------------------")
        except zipfile.BadZipFile:
            print("[carve]   (carved bytes were not a valid zip -- skipping)")
        print("[carve] NOTE: real malware would EXECUTE here. This lab does NOT.")
    if not found:
        print("[carve] no marker-wrapped payload found (nothing smuggled here).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cached_asset.jpg")

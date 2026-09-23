#!/usr/bin/env python3
"""
make_payload.py  —  Build a BENIGN "smuggled" file for the Cybervoid Saga lab.

This reproduces the *mechanic* of cache smuggling with ZERO malware:
  - We create a tiny ZIP whose only content is a harmless text file.
  - We wrap those ZIP bytes between two marker strings (exactly the technique
    the real campaign used with markers bTgQcBpv / mX6o0lBw).
  - We prepend a real JPEG magic header so the file even *looks* like a JPEG,
    and the lab server will serve it as Content-Type: image/jpeg.

Nothing here executes anything. The "payload" is a text file that says so.
"""
import io
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cached_asset.jpg")

# Benign markers (lab stand-ins for the real bTgQcBpv / mX6o0lBw).
START = b"LABSTART"
END = b"LABEND"

# JPEG magic so the file genuinely begins like an image (FF D8 FF).
JPEG_HEADER = bytes([0xFF, 0xD8, 0xFF, 0xE0]) + b"\x00\x10JFIF\x00"

# 1) Build a harmless ZIP entirely in memory.
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr(
        "HELLO_FROM_THE_LAB.txt",
        "This is a BENIGN lab artifact for the Cybervoid Saga documentary.\n"
        "In a real attack this ZIP would hold a loader. Here it holds this note.\n"
        "No code runs. This file only demonstrates cache-smuggling MECHANICS.\n",
    )
zip_bytes = buf.getvalue()

# 2) Smuggle: [jpeg header][decoy][START][zip][END][decoy]
smuggled = (
    JPEG_HEADER
    + b"\n(benign lab image body -- ignore) \n"
    + START + zip_bytes + END
    + b"\n(end of lab asset)\n"
)

with open(OUT, "wb") as f:
    f.write(smuggled)

print(f"[make_payload] wrote {OUT} ({len(smuggled)} bytes)")
print(f"[make_payload] markers: {START.decode()} ... {END.decode()}")
print(f"[make_payload] embedded ZIP: {len(zip_bytes)} bytes, 1 benign text entry")

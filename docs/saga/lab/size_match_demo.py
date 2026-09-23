#!/usr/bin/env python3
"""
size_match_demo.py — BENIGN reproduction of the campaign's size-match cache carve.

Documents *how the extractor works* (Appendix E) WITHOUT any malware:

  Real command (annotated, NOT run here):
    cmd /c for /r "<cache root>" %f in (f_*) do
        @if %~zf==17635 copy "%f" %TEMP%\\t.bat >nul 2>nul && %TEMP%\\t.bat
                                                              ^^^^^^^^^^^^^^  (exec — omitted)

  This script does the same SELECTION-BY-SIZE against a fake cache full of
  harmless files, copies the match out to a .bat-equivalent, and then only
  PRINTS it. Nothing is executed, nothing touches the network.

The point: show that a browser cache entry can be located purely by its exact
byte size, with no download and no marker string.
"""
import os
import random
import shutil
import string

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".fake-cache", "Cache_Data")
TARGET_SIZE = 17635  # the exact size the real campaign matched on
OUT = os.path.join(HERE, ".fake-cache", "t.bat")


def rand_bytes(n):
    return ("".join(random.choice(string.ascii_letters) for _ in range(n))).encode()


def seed_cache():
    shutil.rmtree(os.path.join(HERE, ".fake-cache"), ignore_errors=True)
    os.makedirs(CACHE, exist_ok=True)
    sizes = []
    # A pile of ordinary cache entries of assorted sizes (decoys).
    for i in range(8):
        size = random.choice([512, 2048, 9001, 20000, 4096, 17636, 17634, 65536])
        p = os.path.join(CACHE, f"f_{i:06d}")
        with open(p, "wb") as f:
            f.write(rand_bytes(size))
        sizes.append((os.path.basename(p), size))
    # The ONE seeded "payload": a harmless .bat-like text, padded to EXACTLY TARGET_SIZE.
    body = (
        b"@echo off\r\n"
        b":: BENIGN lab stand-in for the 17,635-byte cached batch.\r\n"
        b":: The real one carved and ran the next stage. This one just says hello.\r\n"
        b"echo [lab] size-match carve succeeded -- this is where the payload WOULD run.\r\n"
    )
    pad = TARGET_SIZE - len(body) - len(b"\r\n:: pad\r\n")
    body += b":: pad\r\n" + (b"#" * pad) + b"\r\n"
    body = body[:TARGET_SIZE]
    payload_name = f"f_{random.randint(100,999):06d}"
    with open(os.path.join(CACHE, payload_name), "wb") as f:
        f.write(body)
    sizes.append((payload_name, len(body)))
    return sizes, payload_name


def carve_by_size(target):
    """The Python equivalent of: for /r (f_*) do @if %~zf==target copy ... """
    for root, _, files in os.walk(CACHE):
        for name in sorted(files):
            if not name.startswith("f_"):
                continue
            full = os.path.join(root, name)
            zf = os.path.getsize(full)          # <-- %~zf
            if zf == target:                    # <-- @if %~zf==17635
                shutil.copy(full, OUT)          # <-- copy "%f" %TEMP%\t.bat
                return full, OUT
    return None, None


def main():
    print(f"[demo] seeding a fake browser cache in {os.path.relpath(CACHE, HERE)} ...")
    sizes, payload_name = seed_cache()
    print("[demo] cache entries (name -> size):")
    for name, size in sizes:
        mark = "  <-- exact match target" if size == TARGET_SIZE else ""
        print(f"          {name}  {size}{mark}")
    print(f"\n[demo] running size-match carve for %~zf=={TARGET_SIZE} ...")
    src, out = carve_by_size(TARGET_SIZE)
    if not src:
        print("[demo] no file matched (unexpected).")
        return 1
    print(f"[demo] MATCH: {os.path.basename(src)} == {TARGET_SIZE} bytes")
    print(f"[demo] copied to: {os.path.relpath(out, HERE)}  (stands in for %TEMP%\\t.bat)")
    print("[demo] the real command would now EXECUTE it. This lab only prints its head:\n")
    with open(out, "rb") as f:
        head = f.read(320).decode(errors="replace")
    for line in head.splitlines()[:6]:
        print("        | " + line)
    print("\n[demo] NOTE: no download, no network, no execution. Selection was by SIZE alone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

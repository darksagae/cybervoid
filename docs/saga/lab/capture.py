#!/usr/bin/env python3
"""
capture.py  —  Drive Chromium through the lab demo and capture real evidence.

Steps:
  1. Launch Chromium with a fresh, throwaway user-data-dir (so we can inspect
     its cache afterwards).
  2. Load the SIMULATED lure page; the hidden <img> makes Chromium cache the
     image/jpeg-labelled asset.
  3. Screenshot the page.
  4. Walk the browser's Cache_Data directory and confirm our benign ZIP (with
     its LABSTART/LABEND markers) really landed on disk inside a cached entry.
  5. Write a short evidence report.

No malware, no execution of carved content -- this only proves the mechanic.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.abspath(os.path.join(HERE, "..", "screenshots"))
PROFILE = os.path.join(HERE, ".lab-profile")
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
URL = "http://127.0.0.1:8099/"
START, END = b"LABSTART", b"LABEND"

from playwright.sync_api import sync_playwright  # noqa: E402


def find_marker_in_cache():
    hits = []
    for base in ("Default/Cache/Cache_Data", "Default/Cache", "Cache/Cache_Data"):
        for path in glob.glob(os.path.join(PROFILE, base, "**", "*"), recursive=True):
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "rb") as f:
                    blob = f.read()
            except OSError:
                continue
            if START in blob and END in blob:
                m = re.search(re.escape(START) + b"(.*?)" + re.escape(END), blob, re.DOTALL)
                hits.append((path, len(blob), len(m.group(1)) if m else 0))
    return hits


def main():
    os.makedirs(SHOTS, exist_ok=True)
    report = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, executable_path=CHROMIUM, headless=True,
            args=["--disk-cache-size=10485760"],
        )
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(800)
        shot = os.path.join(SHOTS, "01-lab-lure-page.png")
        page.screenshot(path=shot)
        report.append(f"screenshot: {shot}")
        # Confirm the asset was actually requested as an image.
        resp = page.request.get(URL + "cached_asset.jpg")
        report.append(f"asset Content-Type: {resp.headers.get('content-type')}")
        report.append(f"asset X-Lab-Tag: {resp.headers.get('x-lab-tag')}")
        ctx.close()

    hits = find_marker_in_cache()
    report.append(f"cache entries containing smuggled markers: {len(hits)}")
    for path, total, carved in hits:
        rel = os.path.relpath(path, PROFILE)
        report.append(f"  cache blob: {rel}  ({total} bytes, {carved} carved)")

    out = os.path.join(HERE, "evidence-report.txt")
    with open(out, "w") as f:
        f.write("Cybervoid Saga — lab evidence report\n")
        f.write("=" * 40 + "\n")
        f.write("\n".join(report) + "\n")
    print("\n".join(report))
    print(f"[capture] report written: {out}")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())

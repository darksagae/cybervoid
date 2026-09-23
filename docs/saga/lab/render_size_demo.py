#!/usr/bin/env python3
"""Render the size-match demo output to a PNG for the saga's evidence set."""
import html
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.abspath(os.path.join(HERE, "..", "screenshots"))


def main():
    txt = open(os.path.join(HERE, ".fake-cache-run.txt")).read()
    page = (
        "<!doctype html><meta charset=utf-8><style>"
        "body{margin:0;background:#0a0e0c;color:#c9f5df;"
        "font:13px/1.5 'DejaVu Sans Mono',monospace;padding:22px}"
        "h2{color:#8b5cf6;font-size:14px;margin:0 0 10px}"
        "pre{white-space:pre-wrap;margin:0}</style>"
        "<h2>CYBERVOID SAGA - size-match cache carve (benign lab run)</h2>"
        f"<pre>{html.escape(txt)}</pre>"
    )
    tmp = os.path.join(HERE, "_size.html")
    open(tmp, "w").write(page)
    out = os.path.join(SHOTS, "06-lab-size-match-carve.png")
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            headless=True,
        )
        pg = b.new_page(viewport={"width": 1000, "height": 20})
        pg.goto("file://" + tmp)
        pg.wait_for_timeout(250)
        pg.screenshot(path=out, full_page=True)
        b.close()
    os.remove(tmp)
    print("rendered", out)


if __name__ == "__main__":
    main()

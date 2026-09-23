#!/usr/bin/env python3
"""Render the lab's text evidence into a single PNG 'terminal' screenshot."""
import html
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.abspath(os.path.join(HERE, "..", "screenshots"))


def read(name):
    p = os.path.join(HERE, name)
    return open(p).read() if os.path.exists(p) else f"(missing {name})"


def main():
    body = html.escape(
        read("evidence-report.txt") + "\n\n"
        + read("carve-from-cache.txt") + "\n"
        + read("hexdump-evidence.txt")
    )
    page_html = (
        "<!doctype html><html><head><meta charset=utf-8><style>"
        "body{margin:0;background:#0a0e0c;color:#c9f5df;"
        "font:13px/1.45 'DejaVu Sans Mono',monospace;padding:22px}"
        "h2{color:#8b5cf6;font-size:14px;margin:0 0 10px;letter-spacing:.06em}"
        "pre{white-space:pre-wrap;margin:0}</style></head><body>"
        "<h2>CYBERVOID SAGA - LAB EVIDENCE (browser cache smuggling, benign)</h2>"
        f"<pre>{body}</pre></body></html>"
    )
    tmp = os.path.join(HERE, "_evid.html")
    open(tmp, "w").write(page_html)
    os.makedirs(SHOTS, exist_ok=True)
    out = os.path.join(SHOTS, "02-lab-cache-evidence.png")
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            headless=True,
        )
        pg = b.new_page(viewport={"width": 1120, "height": 20})
        pg.goto("file://" + tmp)
        pg.wait_for_timeout(300)
        pg.screenshot(path=out, full_page=True)
        b.close()
    os.remove(tmp)
    print("rendered", out)


if __name__ == "__main__":
    main()

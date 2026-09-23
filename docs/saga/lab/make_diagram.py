#!/usr/bin/env python3
"""Render the saga's attack-chain diagram (SVG) to a clean PNG for slot 05."""
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.abspath(os.path.join(HERE, "..", "screenshots"))

W, H = 1280, 980
BG, CARD, LINE = "#0a0e0c", "#0d1512", "#173a2c"
FG, DIM, ORB, RED, AMBER = "#c9f5df", "#5e8f79", "#8b5cf6", "#f871a0", "#ffd36b"

STEPS = [
    ("ACT I — THE LURE", "Compromised site shows a fake\n\"Verify you're human\" / FortiClient page", "T1566 · T1189", ORB),
    ("THE SMUGGLE", "Page serves payload as image/jpeg;\nbrowser CACHES it to disk (ZIP in markers)", "T1036.005 · T1027 · T1074.001", ORB),
    ("ACT II — THE PASTE", "Victim pastes one-liner (ClickFix/FileFix)\nWin+R or Explorer bar — by their own hand", "T1204.002 · T1059.001", RED),
    ("THE CARVE", "Command copies Cache_Data, regex-carves\nbetween markers — NO fresh download", "T1140", RED),
    ("THE STAIRCASE", "obf .bat -> PowerShell stages -> fake CF form\n-> base64 ZIP -> in-memory C# loader", "T1620 · T1027", AMBER),
    ("ACT III — THE LOOT", "Infostealer harvests cookies + creds,\nC2 hidden on-chain (EtherHiding), exfil", "T1539 · T1555.003 · T1041", RED),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(x, y, w, h, title, body, atk, accent):
    lines = body.split("\n")
    body_svg = "".join(
        f'<text x="{x+18}" y="{y+56+i*21}" fill="{FG}" font-size="15">{esc(ln)}</text>'
        for i, ln in enumerate(lines)
    )
    return f"""
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CARD}" stroke="{LINE}"/>
      <rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{accent}"/>
      <text x="{x+18}" y="{y+30}" fill="{accent}" font-size="14" font-weight="700"
            letter-spacing="1.5">{esc(title)}</text>
      {body_svg}
      <text x="{x+18}" y="{y+h-14}" fill="{DIM}" font-size="12" font-family="monospace">{esc(atk)}</text>
    """


def arrow(cx, y1, y2):
    return (f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2-8}" stroke="{ORB}" '
            f'stroke-width="2"/><path d="M{cx-6},{y2-10} L{cx},{y2} L{cx+6},{y2-10} Z" fill="{ORB}"/>')


def build_svg():
    cw, ch, gap = 900, 112, 26
    x = (W - cw) // 2
    y0 = 96
    parts = [
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<text x="{W//2}" y="46" fill="{ORB}" font-size="26" font-weight="800" '
        f'text-anchor="middle" letter-spacing="2">THE CYBERVOID SAGA — ATTACK CHAIN</text>',
        f'<text x="{W//2}" y="72" fill="{DIM}" font-size="14" text-anchor="middle">'
        f'Browser cache smuggling · ClickFix / FileFix · defensive study (defanged)</text>',
    ]
    for i, (t, b, a, c) in enumerate(STEPS):
        y = y0 + i * (ch + gap)
        parts.append(card(x, y, cw, ch, t, b, a, c))
        if i < len(STEPS) - 1:
            parts.append(arrow(W // 2, y + ch, y + ch + gap))
    parts.append(
        f'<text x="{W//2}" y="{H-18}" fill="{DIM}" font-size="12" text-anchor="middle">'
        f'The break point: no site asks you to press Win+R and paste. That one habit ends the chain.</text>'
    )
    body = "".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'font-family="DejaVu Sans, Arial, sans-serif">{body}</svg>')


def main():
    svg = build_svg()
    tmp = os.path.join(HERE, "_diagram.svg")
    open(tmp, "w").write(svg)
    os.makedirs(SHOTS, exist_ok=True)
    out = os.path.join(SHOTS, "05-diagram-attack-chain.png")
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            headless=True,
        )
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + tmp)
        pg.wait_for_timeout(300)
        pg.screenshot(path=out)
        b.close()
    os.remove(tmp)
    print("rendered", out)


if __name__ == "__main__":
    main()

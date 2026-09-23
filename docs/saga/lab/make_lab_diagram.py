#!/usr/bin/env python3
"""Render the Appendix G isolated-detonation-lab network diagram to PNG."""
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.abspath(os.path.join(HERE, "..", "screenshots"))

W, H = 1280, 760
BG, CARD, LINE = "#0a0e0c", "#0d1512", "#173a2c"
FG, DIM, ORB, RED, GREEN, AMBER = "#c9f5df", "#5e8f79", "#8b5cf6", "#f871a0", "#34c55e", "#ffd36b"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, accent, title, lines, tcol=None):
    body = "".join(
        f'<text x="{x+18}" y="{y+56+i*22}" fill="{FG}" font-size="14">{esc(t)}</text>'
        for i, t in enumerate(lines)
    )
    return f"""
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CARD}" stroke="{LINE}"/>
      <rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{accent}"/>
      <text x="{x+18}" y="{y+30}" fill="{tcol or accent}" font-size="15" font-weight="700"
            letter-spacing="1">{esc(title)}</text>
      {body}
    """


def svg():
    p = [
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<text x="{W//2}" y="46" fill="{ORB}" font-size="24" font-weight="800" '
        f'text-anchor="middle" letter-spacing="1.5">APPENDIX G — ISOLATED DETONATION LAB</text>',
        f'<text x="{W//2}" y="72" fill="{DIM}" font-size="14" text-anchor="middle">'
        f'Host-only network · NO route to the internet · the C2 fetch is answered inside the lab</text>',
    ]

    # Isolation boundary
    p.append(f'<rect x="60" y="100" width="{W-120}" height="470" rx="16" fill="none" '
             f'stroke="{RED}" stroke-width="2" stroke-dasharray="8 6"/>')
    p.append(f'<text x="80" y="126" fill="{RED}" font-size="13" font-weight="700">'
             f'ISOLATION BOUNDARY — host-only vSwitch, no NAT/bridge</text>')

    # Victim VM (left)
    p.append(box(110, 160, 470, 200, ORB, "VICTIM VM — FLARE-VM (Windows 10)", [
        "IP 10.0.0.10   ·   gateway+DNS = 10.0.0.2",
        "Runs the sample (ClickFix paste / t.bat)",
        "Sysmon · PowerShell ScriptBlock Logging (4104)",
        "Procmon · Process Hacker · RegShot",
        "Snapshot: clean-victim  (revert after run)",
    ]))

    # Services VM (right)
    p.append(box(700, 160, 470, 200, GREEN, "SERVICES VM — REMnux (Linux)", [
        "IP 10.0.0.2  (fake gateway + DNS)",
        "INetSim / FakeNet-NG  = simulated internet",
        "answers EVERY domain/IP the malware calls",
        "tcpdump / Wireshark  -> detonation.pcap",
        "Snapshot: clean-services",
    ], tcol=GREEN))

    # Arrows between VMs
    midy = 235
    p.append(f'<line x1="580" y1="{midy}" x2="700" y2="{midy}" stroke="{AMBER}" stroke-width="2"/>')
    p.append(f'<path d="M694,{midy-6} L700,{midy} L694,{midy+6} Z" fill="{AMBER}"/>')
    p.append(f'<text x="640" y="{midy-10}" fill="{AMBER}" font-size="12" text-anchor="middle">irm C2</text>')
    midy2 = 300
    p.append(f'<line x1="700" y1="{midy2}" x2="580" y2="{midy2}" stroke="{GREEN}" stroke-width="2"/>')
    p.append(f'<path d="M586,{midy2-6} L580,{midy2} L586,{midy2+6} Z" fill="{GREEN}"/>')
    p.append(f'<text x="640" y="{midy2-10}" fill="{GREEN}" font-size="12" text-anchor="middle">fake reply</text>')

    # Real internet / C2 — blocked
    p.append(box(700, 400, 470, 120, RED, "REAL C2 / INTERNET", [
        "45.39.216[.]46/velcap3d  (never contacted)",
        "request is captured at 10.0.0.2, not forwarded",
    ], tcol=RED))
    # blocked link from boundary to internet
    p.append(f'<line x1="{W//2}" y1="570" x2="{W//2}" y2="400" stroke="{RED}" stroke-width="2" stroke-dasharray="4 5"/>')
    p.append(f'<circle cx="{W//2}" cy="485" r="17" fill="none" stroke="{RED}" stroke-width="3"/>')
    p.append(f'<line x1="{W//2-12}" y1="497" x2="{W//2+12}" y2="473" stroke="{RED}" stroke-width="3"/>')
    p.append(f'<text x="{W//2+28}" y="490" fill="{RED}" font-size="13" font-weight="700">BLOCKED — no egress</text>')

    # Bottom flow
    p.append(f'<text x="{W//2}" y="620" fill="{DIM}" font-size="13" text-anchor="middle">'
             f'detonate → observe (carve %~zf==17635 → conhost --headless → powershell irm/iex) '
             f'→ collect artifacts → REVERT snapshots</text>')
    p.append(f'<text x="{W//2}" y="650" fill="{FG}" font-size="14" text-anchor="middle" font-weight="700">'
             f'Same command as the wild — opposite blast radius: the C2 request never leaves the lab.</text>')
    p.append(f'<text x="{W//2}" y="700" fill="{DIM}" font-size="11" text-anchor="middle">'
             f'Cybervoid Saga · Appendix G · methodology only — not run in this repo\'s environment</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'font-family="DejaVu Sans, Arial, sans-serif">{"".join(p)}</svg>')


def main():
    tmp = os.path.join(HERE, "_lab.svg")
    open(tmp, "w").write(svg())
    out = os.path.join(SHOTS, "07-detonation-lab-network.png")
    with sync_playwright() as pw:
        b = pw.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", headless=True)
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + tmp)
        pg.wait_for_timeout(300)
        pg.screenshot(path=out)
        b.close()
    os.remove(tmp)
    print("rendered", out)


if __name__ == "__main__":
    main()

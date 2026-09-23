# Screenshots & Captured Evidence

This folder holds the **visual record** of the saga: frames from the source video, disk/
forensic captures, and diagrams used in the book and documentary. It is intentionally
committed with a capture guide first, so the evidence set can be filled in reproducibly.

## Naming convention

```
NN-source-description.ext
```
- `NN` — two-digit order (matches appearance in the book/film).
- `source` — `hammond` (video), `sensepost`, `doublecup`, `lab`, `diagram`.
- `description` — short kebab-case label.

Examples:
```
01-hammond-fake-cloudflare-prompt.png
02-hammond-run-box-oneliner.png
03-sensepost-nginx-default-type.png
04-lab-chromium-cache_data-hexdump.png
05-diagram-attack-chain.png
```

## Capture plan (reproducible)

### A. From the John Hammond video (attribute on every frame)
Capture these beats (see [Chapter 1](../chapter-01-the-infected-cache.md)):
1. The fake "Verify you're human" / Cloudflare prompt (the lure).
2. The ClickFix instruction to press `Win+R` and paste.
3. The one-liner that reads from the browser cache.
4. The obfuscated batch stage.
5. The PowerShell-rendered fake Cloudflare form.
6. The base64 ZIP / inline C# loader.
7. The infostealer's cookie/history collection.

> **Fair-use / attribution:** each captured frame must carry an on-image credit
> ("Source: John Hammond — *My Browser Cache Got Infected*") and is used here for
> commentary and education. Prefer linking/timestamping over wholesale re-hosting.

### B. Lab-safe forensic captures (no live malware)
Reproduce the *benign* mechanics for teaching visuals:
- A hex view of a Chromium `Cache_Data/f_######` entry showing image header vs. body.
- A Firefox `cache2\entries\` file showing embedded HTTP headers.
- An EDR/Sysmon event of `explorer.exe → powershell.exe` (simulated, benign command).

Build these with a **simulated** page that caches a harmless file — never a real payload.
See the documentary [shot list](../documentary/shot-list.md) for the safe-demo spec.

### C. Diagrams
Export the ASCII chain diagrams from the chapters as clean vector/PNG for the film.

## Status

| Slot | File | Status |
|------|------|--------|
| 01 | **01-lab-lure-page.png** | ✅ **Captured** — real Chromium render of the SIMULATED lure ([lab/](../lab/)) |
| 02 | **02-lab-cache-evidence.png** | ✅ **Captured** — terminal proof: ZIP served as `image/jpeg` landed in `Cache_Data`, carved back out |
| 03 | hammond-fake-cloudflare-prompt | ⏳ to capture from the video (human pass) |
| 04 | hammond-run-box-oneliner | ⏳ to capture from the video (human pass) |
| 05 | **05-diagram-attack-chain.png** | ✅ **Rendered** — the full chain with ATT&CK IDs per stage (from `lab/make_diagram.py`) |

**Slots 01–02 are real, committed captures** produced by the runnable lab in
[`../lab/`](../lab/README.md) — see [`../lab/evidence-report.txt`] after a run. They are
fully benign (no malware) and ready for the documentary. Slots 03–04 need a human to grab
frames from the source video (YouTube blocks automated capture).

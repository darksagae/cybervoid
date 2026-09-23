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
| 04 | *(video frames — see below)* | ✅ **Captured** in [`video/`](video/) |
| 05 | **05-diagram-attack-chain.png** | ✅ **Rendered** — the full chain with ATT&CK IDs per stage (from `lab/make_diagram.py`) |

**Slots 01–02** are real, committed lab captures (benign). **Slot 05** is the rendered
diagram.

### Video frames — ✅ captured & documented ([`video/`](video/))

12 frames from John Hammond's *"My Browser Cache Got Infected"* are committed under
[`video/`](video/) and documented frame-by-frame in
[Appendix E](../appendix-e-frames.md). Used for defensive commentary/education, credited to
John Hammond.

| File | Shows |
|------|-------|
| `01-lure-cloudflare-clickfix.png` | the `smilesofboca` compromised site + fake Cloudflare ClickFix box |
| `02-clipboard-size-match-extractor.png` | the pasted command (`%~zf==17635` → `t.bat`) in Sublime |
| `03-stage2-c2-beacon.png` | `stage2.ps1`: `irm`+`iex` to randomized/fallback C2 |
| `04`–`12` `*-fake-cf-*` | the PowerShell-rendered fake "Cloudflare Security Challenge" form |

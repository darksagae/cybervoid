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
| 01 | hammond-fake-cloudflare-prompt | ⏳ to capture |
| 02 | hammond-run-box-oneliner | ⏳ to capture |
| 03 | sensepost-nginx-default-type | ⏳ to capture |
| 04 | lab-chromium-cache_data-hexdump | ⏳ to build (lab-safe) |
| 05 | diagram-attack-chain | ⏳ to export |

*No binary images are committed yet — this guide defines the set so captures can be added
consistently as the saga is filmed.*

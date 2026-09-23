# THE CYBERVOID SAGA
### A Field Book of Cyber-Research — Recorded, Documented, and Retold

> *"Every infection tells a story. This book records the ones we chase into the void."*

This is a living **book of records** — a documented saga of cyber-security research.
It begins with a single investigation by researcher **John Hammond** ("My Browser
Cache Got Infected") and expands outward into the wider technique, its history, the
threat actors who weaponized it, and how defenders hunt it.

Everything here is written for **defensive and educational** purposes: understanding
attacker tradecraft so it can be detected, disrupted, and taught. All live indicators
and offensive commands are **defanged** (neutralized) so the book can be read, shared,
and filmed safely.

---

## How to read this book

| # | Part | What it covers |
|---|------|----------------|
| — | [Preface](00-preface.md) | The mission, scope, and rules of the saga |
| — | [Research Log](research-log.md) | *How* the research was made — every step, source, and dead end |
| 1 | [Chapter 1 — The Infected Cache](chapter-01-the-infected-cache.md) | John Hammond's investigation, scene by scene |
| 2 | [Chapter 2 — Cache Smuggling](chapter-02-cache-smuggling.md) | The technique itself, in technical depth |
| 3 | [Chapter 3 — The Ecosystem](chapter-03-the-ecosystem.md) | ClickFix, DOUBLECUP, EXIF smuggling, FileFix |
| 4 | [Chapter 4 — The Marketplace](chapter-04-the-marketplace.md) | DOUBLECUP loader-as-a-service (Episode 2) |
| 5 | [Chapter 5 — The Defense](chapter-05-the-defense.md) | Defender's playbook, FileFix, IR (Episode 3) |
| A | [Appendix A — Artifacts](appendix-a-artifacts.md) | Defanged code, IOCs, cache paths |
| B | [Appendix B — Detection & Hunting](appendix-b-detection.md) | Detection logic, hunt queries, forensics |
| C | [Appendix C — The Files, Documented](appendix-c-the-files.md) | Every file Hammond covered: role, structure, defanged reconstruction |
| D | [Appendix D — ATT&CK Mapping](appendix-d-attack-mapping.md) | Every artifact mapped to MITRE ATT&CK + a coverage matrix |
| E | [Appendix E — Frame-by-Frame](appendix-e-frames.md) | The video's actual frames: the `smilesofboca` lure, the size-match extractor, the C2 beacon, the fake Cloudflare form |
| — | [Lab](lab/) | **Runnable, benign** reproduction of the cache-smuggling mechanic |
| — | [Sources](sources.md) | Full bibliography with links |
| — | [Documentary](documentary/) | Treatment, script, and shot list for the film |
| — | [Screenshots](screenshots/) | Captured evidence (real lab screenshots) + capture guide |

---

## The saga at a glance

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  ACT I   A compromised website shows a fake "Verify you're human" │
  │          Cloudflare / CAPTCHA prompt.  (ClickFix lure)            │
  │                                                                   │
  │  ACT II  The page quietly writes its next stage into the          │
  │          victim's BROWSER CACHE, disguised as an image.           │
  │                                                                   │
  │  ACT III The victim is told to paste a "fix" into the Run box.    │
  │          The one-liner pulls the payload back OUT of the cache —  │
  │          no fresh download, no obvious network fetch.             │
  │                                                                   │
  │  ACT IV  Obfuscated batch → PowerShell stages → in-memory C#      │
  │          shellcode loader → infostealer exfiltrates the browser.  │
  └──────────────────────────────────────────────────────────────────┘
```

The twist that gives the saga its name: **the browser's own cache becomes the
malware delivery mechanism.** The thing meant to make the web faster becomes the
smuggler's suitcase.

---

## Status of the record

| Part | Status |
|------|--------|
| Chapters 1–5 | ✅ Drafted |
| Appendices A–B | ✅ Drafted |
| Appendix C (the files/artifacts) | ✅ Drafted with recovered IOCs |
| Appendix D (ATT&CK mapping) | ✅ Drafted |
| Runnable lab (benign reproduction) | ✅ Built & executed |
| Sources | ✅ Compiled |
| Documentary treatment & Ep.1 script | ✅ Drafted |
| Screenshots / captured evidence | ✅ Lab captures + **12 documented video frames** ([screenshots/video/](screenshots/video/)) |

This book is versioned in git. Each research session adds to the record; see the
[Research Log](research-log.md) for the running history.

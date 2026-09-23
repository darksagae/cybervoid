# Research Log — How This Saga Was Made

This log records the *process* of the investigation: the queries run, the sources
opened, what each yielded, and how the trail branched. It is the "making-of" track
that runs alongside the book. Entries are append-only.

Environment: research conducted inside a Claude Code cloud session in the `cybervoid`
repository. Web access via search + fetch tools. All findings cross-checked against
primary sources listed in [sources.md](sources.md).

---

## Session 001 — Identifying the origin video

**Goal:** Identify the John Hammond video at `youtu.be/oJHOlNTH7lY` and establish the
saga's subject.

1. **Direct page fetch** of the YouTube watch URL → **blocked** (302 redirect to
   Google's anti-bot "sorry" interstitial). *Dead end #1 — expected; YouTube rate-limits
   automated fetches.*
2. **Pivot to oEmbed.** Queried `youtube.com/oembed?url=...&format=json`.
   → **Hit.** Returned:
   - Title: **"My Browser Cache Got Infected"**
   - Author: **John Hammond** (`youtube.com/@_JohnHammond`)
   - Thumbnail: `i.ytimg.com/vi/oJHOlNTH7lY/hqdefault.jpg`
3. **Cross-check** via `noembed.com` → same metadata. Identity confirmed.

**Outcome:** Subject established — a browser-cache malware investigation. The video's
title becomes the title of Chapter 1.

---

## Session 002 — Mapping the technique

**Goal:** Understand the technique the video analyzes and place it in the literature.

1. **Search:** *John Hammond "My Browser Cache Got Infected" malware browser cache research.*
   → Surfaced the through-line: a **ClickFix** lure using a fake Cloudflare "verify
   you're human" Turnstile prompt that **smuggles a batch script into the browser
   cache** (Firefox/Chrome/Brave selected by user-agent), then instructs the victim to
   run a one-liner that pulls the payload *out of the cache* instead of downloading it.
   Chain: obfuscated batch → PowerShell stages → lookalike domains / disguised IPs →
   fake PowerShell-rendered Cloudflare form → base64 zip with inline C# shellcode
   loader → infostealer exfiltrating cookies + history.
2. **Search:** *malware hiding payload in browser cache file disk analysis technique.*
   → Anchored the technique to its literature:
   - **SensePost (2023)** — original "browsers' cache smuggling."
   - **MalwareTech (2025)** — "Passively Downloading Malware Payloads Via Image
     Caching" (EXIF smuggling).
   - **BleepingComputer / SOCRadar (2026)** — **DOUBLECUP** ClickFix service hiding
     malware in cached PNGs.
   - **CyberMaxx, Arete** — analyst write-ups and detection framing.

**Outcome:** The saga's spine is confirmed: origin (2023) → evolution (2025) →
industrialization (2026), with the Hammond video as the human-guided walkthrough.

---

## Session 003 — Primary-source deep read

**Goal:** Pull technical specifics from primary sources for Chapters 2–3 and appendices.

1. **Fetched SensePost (Aurelien Chalot, 2023-07-10).** Extracted:
   - The nginx `default_type image/jpeg` + nulled MIME-map trick that forces caching.
   - `<img>` tag pointing at a DLL → browser caches it under a random, extension-less name.
   - Disk locations: Firefox `...\Firefox\Profiles\<p>\cache2\entries\` (with HTTP
     metadata preserved); Chrome `...\Chrome\User Data\Default\Cache\Cache_Data\`
     (binary DB).
   - Retrieval: custom HTTP header tag (e.g. `Tag: DLLHERE`) for Firefox; `INDLL`/
     `OUTDLL` wrapper + regex carve for Chrome; execution via `rundll32` without a
     `.dll` extension.
2. **Fetched BleepingComputer on DOUBLECUP (2026).** Extracted:
   - Loader-as-a-service, active since early June 2026; hides code in **PNG** cache.
   - Delivers **CountLoader** (stealer) and **DeviceManager** (Python RAT using
     blockchain smart contracts / EtherHiding for C2 lookup).
   - Victim commands search cache **by file size**, carve with `findstr` / `certutil`.
   - Discovery: SOCRadar found an open directory at `213.139.77[.]109:9090` (Aug 2026).

**Outcome:** Enough primary detail to write the technical chapters and the defanged
artifact appendix. Remaining gap: frame-accurate screenshots from the video (captured
evidence) — see [screenshots/README.md](screenshots/README.md) for the capture plan.

---

## Session 004 — Recovering the actual files Hammond covered

**Goal:** Document the *specific files* walked through in the video (user request: "he
covered the files, we need them for full documentation").

1. **Search** for the campaign's file-level artifacts → surfaced **Expel's** writeup
   (*"Cache smuggling: When a picture isn't a thousand words,"* by **Marcus Hutchins /
   MalwareTech**) as the primary file-level source, plus a GBHackers summary.
2. **WebFetch of Expel** → returned "content truncated"; **WebFetch of GBHackers** →
   returned empty (JS-gated). *Dead ends #2 and #3.*
3. **Pivot to raw `curl`.** Expel page is a heavy JS bundle; piped through `sed`/`grep` to
   carve the article prose from the persisted 1.1 MB response.
   → **Recovered the real, deobfuscated one-liner** and the full carve chain:
   - Lure = **FileFix / Fortinet FortiClient VPN compliance** (not Cloudflare in this
     variant); decoy path `\\Public\Support\VPN\ForticlientCompliance.exe`.
   - Clipboard command padded with **139 leading spaces**, run "headless" via conhost.
   - Copies all of Chrome `Cache_Data`, `[regex]::Matches` carve **between markers
     `bTgQcBpv` and `mX6o0lBw`**, writes `ComplianceChecker.zip`, `Expand-Archive`, then
     runs `FortiClientComplianceChecker.exe`.
4. **Fetched Hammond's `recaptcha-phish` GitHub** (raw README) → his benign reproduction of
   the lure front end (`index.html` + `calc.exe` HTA), the cleanest way to study Artifact [1].

**Outcome:** Wrote **[Appendix C — The Files, Documented](appendix-c-the-files.md)**: each
artifact's role, structure, and a **defanged/neutralized** reconstruction, with the real
(already-public) IOC markers preserved for detection. Reconciled the ClickFix-Cloudflare vs.
FileFix-Fortinet lure costumes in Chapter 1 and Appendix C §C.0.

**Ethics note recorded:** the one-liner is reproduced from a public vendor writeup, annotated
for analysis, with the final execution line disabled (`<REDACTED>`); the chain is inert with
no attacker-hosted cached image.

## Session 005 — Building the lab & capturing real evidence

**Goal:** Reproduce the cache-smuggling *mechanic* safely, capture genuine screenshots, and
map every artifact to MITRE ATT&CK.

1. **Built a benign lab** (`docs/saga/lab/`): `make_payload.py` wraps a harmless ZIP (one
   text note) between markers `LABSTART`/`LABEND` behind a real JPEG header; `server.py`
   serves it as `Content-Type: image/jpeg`; `index.html` is a SIMULATED lure whose hidden
   `<img>` forces caching; `carve.py` reproduces the carve step but only **prints** (never
   executes); `capture.py` drives headless Chromium and inspects its cache.
2. **Ran it end-to-end.** Installed `playwright`, used the environment's Chromium at
   `/opt/pw-browsers/chromium-1194/...`. Result: the asset was served `image/jpeg`, and the
   marker-wrapped ZIP **landed in Chromium's real cache** at
   `Default/Cache/Cache_Data/d3c0ba3e19ba03b9_0` (859 bytes, 302 carved). `carve.py` pulled
   the benign ZIP back out. `file(1)` even misreports the asset as "JPEG image data" —
   proving the disguise. *This is the whole saga, harmless and in miniature.*
3. **Captured evidence** → `screenshots/01-lab-lure-page.png` (rendered lure) and
   `screenshots/02-lab-cache-evidence.png` (terminal proof), plus `lab/evidence-report.txt`.
4. **Wrote [Appendix D — ATT&CK Mapping](appendix-d-attack-mapping.md):** every step/IOC
   mapped to techniques (T1036.005, T1027, T1074.001, T1204.002, T1059.001, T1140, T1053.005,
   T1539, T1555.003, T1568.003, T1041, …) with a coverage matrix and detection-priority order.

**Outcome:** The documentary now has real, benign screenshots; defenders have a runnable
teaching demo and an ATT&CK coverage sheet. Runtime junk is git-ignored; screenshots +
scripts + README are the durable record.

## Session 006 — Episode 2, repo wiring, and PR

**Goal:** Extend the saga (Chapter 4), surface it from the repo root, and open a PR.

1. **Wrote [Chapter 4 — The Marketplace](chapter-04-the-marketplace.md)** (Episode 2): the
   DOUBLECUP loader-as-a-service story — how the technique became a rentable product
   (hosted steganographic PNGs, per-victim keys, auto-rebuilt payloads), its size-based
   cache-carve chain, the IP-derived decryption key as anti-analysis, CountLoader +
   DeviceManager (EtherHiding C2), and the open-directory (`213.139.77[.]109:9090`) that
   SOCRadar pulled to unravel it.
2. **Created a root `README.md`** (none existed) introducing the platform and featuring the
   saga with a full navigation table.
3. **Opened a PR** from `claude/cyber-research-documentation-p94xvu` into `master`.

## Open threads (to chase in future sessions)

- [ ] Frame-by-frame capture of the Hammond video for the screenshot evidence set.
- [ ] Map the observed IOCs to MITRE ATT&CK technique IDs (T1105, T1204, T1027, etc.).
- [ ] Pull the CyberMaxx and Arete write-ups for a second detection viewpoint.
- [ ] Cross-reference FileFix vs ClickFix lure variants.
- [ ] Build a lab-safe, fully-simulated demo (no live payload) for the documentary.

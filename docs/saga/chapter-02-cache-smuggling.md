# Chapter 2 — Cache Smuggling, Mechanically

> Primary source: **Aurelien Chalot (SensePost)**, *"Browsers' cache smuggling"*,
> 2023-07-10. Corroborated by CyberMaxx, Arete, and the campaign reporting in
> [Chapter 3](chapter-03-the-ecosystem.md). **All specifics here are defensive.**
> Offensive steps are described at a conceptual level and any command is defanged.

---

## 2.1 The core idea in one sentence

A web server can convince a browser to **save an arbitrary file to disk as if it were a
cached image**, and later something on the machine can **read that file back and run it** —
so the "download" of the malware is laundered through normal, trusted caching.

## 2.2 Why browsers cooperate

Browsers cache static resources to make the web fast. Two behaviors combine into the trick:

1. **Content-Type drives handling, not the file's real bytes.** If a server labels a
   response `Content-Type: image/jpeg`, the browser treats the response as an image to be
   fetched and cached — regardless of what the bytes actually are.
2. **`<img>` forces a fetch.** An `<img src="...">` tag makes the browser retrieve and
   cache the resource automatically on page load, no click required.

So a page with an `<img>` pointing at a file the server *claims* is a JPEG will pull that
file down and write it into the cache. If the bytes are actually a DLL, a script, or a ZIP,
the browser neither knows nor cares.

> **The SensePost server trick (conceptual):** in the original write-up the nginx config
> nulls the normal MIME-type map and sets `default_type image/jpeg` for a location, so
> *every* file served from it is announced as an image. The malicious DLL is then just
> another "image" the browser happily caches.

## 2.3 Where the smuggled file lands (disk forensics)

This is the part defenders care about most — because it's where the evidence lives.

| Browser | Cache location (Windows) | Storage form |
|---------|--------------------------|--------------|
| **Firefox** | `AppData\Local\Mozilla\Firefox\Profiles\<profile>\cache2\entries\` | One file per cached entry; **HTTP response metadata (headers) preserved** alongside the body |
| **Chrome / Chromium / Brave** | `...\<Browser>\User Data\Default\Cache\Cache_Data\` | Entries packed into **binary cache database blocks** (`data_#`, `f_######`) |

Two consequences:

- The cached file has **no meaningful extension** and a **randomized name** — so
  extension- and name-based signatures miss it.
- Firefox keeps the **original HTTP headers** with each entry. That's a gift to *attackers*
  (they can tag their file with a custom header to find it again) and a gift to *defenders*
  (those same headers are an artifact you can hunt).

## 2.4 Finding the needle again (retrieval)

The smuggled file is now one of hundreds of cache blobs. The attacker needs to relocate
*their* file without knowing its random name. Documented approaches (defanged, conceptual):

- **Firefox — header tagging.** The server adds a **custom HTTP header** (the write-up used
  something like `Tag: DLLHERE`). Because Firefox stores headers with the entry, a script
  greps the `cache2\entries\` files for that unique header string to find the right blob.
- **Chrome — content wrapping.** The payload is bracketed with unique marker strings (e.g.
  `INDLL` … `OUTDLL`). A script scans the binary cache DB with a regex and **carves** the
  bytes between the markers back out.
- **DOUBLECUP-era variants — size + carving.** Later campaigns locate the entry by **file
  size**, then extract with living-off-the-land tools like `findstr` or `certutil`
  (see [Chapter 3](chapter-03-the-ecosystem.md)).

Once carved out, the bytes are written to a normal file and executed — historically via
`rundll32` pointed at the DLL **without** a `.dll` extension (another small evasion), or,
in the ClickFix chains, handed to a batch/PowerShell stage.

## 2.5 What this evades, and what it doesn't

**Evades:**
- Network detections keyed on "script downloads payload at execution time" — the transfer
  already happened during page load, disguised as an image.
- Signature/extension checks on disk — the artifact is an extension-less cache blob.
- Some proxy/content filters — the content was labeled `image/jpeg`.

**Does *not* evade (the defender's openings):**
- **The write to cache still happens.** An image-typed response whose bytes are a
  PE/DLL/ZIP is anomalous and detectable at the proxy or on disk.
- **The retrieval is noisy.** A process grepping the browser cache directory, or `certutil`/
  `findstr` reading `Cache_Data`, is highly unusual behavior.
- **The manual step is loud.** ClickFix requires `Win+R` → paste → Enter; `explorer.exe`
  spawning `cmd`/`powershell` with a cache path in the command line is a strong signal.
- **Execution still lands somewhere.** `rundll32`/PowerShell touching a file freshly written
  out of a cache directory is a hunt-able sequence.

[Appendix B](appendix-b-detection.md) turns each of these openings into concrete detection
logic.

## 2.6 The forensic through-line

If you only remember one thing from this chapter as an investigator:

> **The malware's first home on the victim's disk is the browser cache, and the cache keeps
> receipts.** Firefox keeps the HTTP headers; Chromium keeps the entry in its cache DB with
> timestamps. Even a "fileless" in-memory finale usually has a **cache-write ancestor** you
> can find.

Next: [Chapter 3 — The Ecosystem](chapter-03-the-ecosystem.md), where this 2023 technique
becomes a 2026 criminal service.

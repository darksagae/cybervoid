# Shot List — Episode 1: "The Infected Cache"

Scene-by-scene production notes. **Golden rule:** nothing on screen is a working attack.
Every terminal is simulated; every indicator is defanged (`[.]`, `hxxp`, `REDACTED`).

Legend: **VO** = narration over · **OTS** = on-screen text · **SIM** = simulated/benign capture.

---

| # | Time | Visual | Capture / build notes | Source |
|---|------|--------|------------------------|--------|
| 1 | 0:00 | Push into pulsing "Verify you're human" box | SIM — build a static mock page; do NOT use a real malicious site | build |
| 2 | 0:20 | Title card *THE INFECTED CACHE* + ethics lower-third | Motion graphic; Cybervoid purple-orb palette | design |
| 3 | 0:50 | Ordinary website loads | SIM — any benign local page | build |
| 4 | 1:30 | **Cache-as-locker** animation: browser files an "image" | Motion graphic | design |
| 5 | 2:10 | OTS: `Content-Type: image/jpeg` → *(bytes say: not an image)* | Text card | design |
| 6 | 2:40 | Fake prompt flips to "verification failed" + Win+R steps | SIM mock page | build |
| 7 | 3:30 | OTS defanged one-liner reading from cache (`# REDACTED`) | Text card only — never a runnable command | design |
| 8 | 4:40 | **Descending staircase** animation, 5 steps light up | Motion graphic; mirror [Ch.1 §1.4](../chapter-01-the-infected-cache.md) diagram | design |
| 9 | 5:30 | Beat: PowerShell "redraws" the fake Cloudflare box | SIM — static mock, labeled *simulated* | build |
| 10 | 6:00 | Cookie-jar-being-emptied graphic (infostealer) | Motion graphic | design |
| 11 | 6:40 | Split screen: Firefox `cache2\entries\` vs Chrome `Cache_Data\` | **SIM lab capture** — see Lab Spec below | lab |
| 12 | 7:30 | Hex view: image header vs. non-image body in a cache blob | **SIM lab capture** with a *harmless* seeded file | lab |
| 13 | 8:40 | Timeline 2023 → 2025 → 2026 | Motion graphic | design |
| 14 | 9:20 | OTS: *DOUBLECUP — LaaS — cached PNGs — CountLoader + DeviceManager* | Text card | design |
| 15 | 10:20 | "Every normal thing became a hiding place" montage (cache/image/click/chain) | Motion graphic | design |
| 16 | 11:40 | SOC screen; one alert lights up | SIM — mock SIEM/EDR alert card | build |
| 17 | 12:20 | **The rule**, full-screen: no site asks you to Win+R + paste | Text card (the payoff) | design |
| 18 | 12:50 | "It needs *you* to open the locker" — return to locker graphic | Motion graphic callback | design |
| 19 | 13:00 | Credits + ethics card | Motion graphic | design |

---

## Lab Spec — safe simulation for shots 11–12

Goal: film the *mechanics* of caching with **zero malware**.

1. **Seed a harmless file.** Serve a small text/PNG file from a local web server with an
   `image/jpeg` Content-Type header (the file can literally say `THIS IS A BENIGN DEMO`).
2. **Load it via `<img>`** on a local page so the browser caches it. Use throwaway profiles.
3. **Show it landing:**
   - Firefox: open `...\Firefox\Profiles\<p>\cache2\entries\`; show the entry with its
     embedded headers (the demo header + `Content-Type: image/jpeg`).
   - Chrome: open `...\Chrome\User Data\Default\Cache\Cache_Data\`; show `f_######` / `data_#`.
4. **Hex view:** open the cached blob in a hex editor to show the header/label vs. the benign
   body bytes. Annotate where a real payload's `MZ`/`PK` magic *would* appear — **do not use
   a real payload.**
5. **EDR beat (optional):** with Sysmon, run a *benign* `explorer → powershell` that reads a
   demo file from the cache dir and prints a harmless string; capture the process event to
   illustrate shot 16's alert. No network egress, no real tooling.

> Everything above is reproducible on a clean VM you then discard. Label all captures
> *SIMULATED* on-screen. See [../screenshots/README.md](../screenshots/README.md) for
> file-naming and the evidence tracker.

## Music & pacing

- Act I: sparse, curious. Act II: mechanical, building. Act III: wider, ominous.
  Coda: resolve to calm — the film ends on empowerment, not dread.

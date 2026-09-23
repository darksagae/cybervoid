# Preface — The Mission

## Why a "saga"?

Malware analysis is rarely a single fact. It is a *chase*: a lure leads to a script,
a script to another stage, a stage to an actor, an actor to a marketplace. Told in
order, that chase reads like a story — a saga — with acts, turns, and a cast. This
book records one such saga and the research that reconstructed it.

The saga opens with a video by **John Hammond**, a malware-analysis researcher and
educator (Huntress; YouTube `@_JohnHammond`), titled **"My Browser Cache Got
Infected."** In it he pulls apart a real-world attack that hides its payload inside
the web browser's cache. From that single thread we follow the technique — **browser
cache smuggling** — back to its documented origins and forward into the criminal
services that industrialized it.

## Scope and intent

- **Defensive and educational only.** The purpose is detection, forensics, teaching,
  and awareness. Nothing here is a build guide for an attack.
- **Everything is defanged.** Domains, IPs, hashes, and commands are neutralized:
  `hxxp://`, `[.]`, spacing, and `REDACTED`/placeholder tokens replace anything that
  could be copy-pasted into harm. The *shape* of the tradecraft is preserved; the
  *loaded weapon* is not.
- **Sourced.** Every claim traces to a public source listed in [sources.md](sources.md).
  Where a source is a video, we cite it by title and channel; where it is a blog or
  vendor report, by author and date.
- **Reproducible record.** The [Research Log](research-log.md) documents how each
  finding was reached so the saga can be audited, corrected, and extended.

## The rules of the record

1. **Record the process, not just the result.** A dead end is part of the saga.
2. **Attribute carefully.** Researchers get credit; actors get described, not admired.
3. **Defang before you write it down.** If it can run, it doesn't go in raw.
4. **Prefer primary sources.** The original researcher's write-up beats a summary of it.
5. **Keep it teachable.** If a chapter can't be shown on screen safely, rewrite it.

## Cast of the saga

| Role | Who / What |
|------|-----------|
| The narrator-investigator | **John Hammond** — walks the original infection |
| The technique's documenter | **Aurelien Chalot (SensePost)** — named "cache smuggling," 2023 |
| The evolution | **MalwareTech** — EXIF/image "passive download" smuggling, 2025 |
| The industrialization | **DOUBLECUP** — loader-as-a-service using cached PNGs, 2026 |
| The lure family | **ClickFix / FileFix** — fake CAPTCHA "paste this to continue" |
| The defenders | Huntress, SOCRadar, CyberMaxx, Arete, and the analysts who hunt it |

Turn the page to the [Research Log](research-log.md) to see how the trail was walked,
or jump straight to [Chapter 1](chapter-01-the-infected-cache.md).

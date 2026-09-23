# Documentary Treatment — "THE INFECTED CACHE"

*A short-form documentary based on The Cybervoid Saga.*

---

## Logline

When a routine "prove you're human" box turns out to be a trap, one investigation reveals
how attackers turned the web browser's own memory — its cache — into a smuggler's suitcase,
and got victims to open it with their own hands.

## Format

- **Type:** Explainer documentary (defensive-security education).
- **Length:** ~12–16 min single episode, or a 3-part micro-series (4–6 min each).
- **Tone:** Investigative, calm, a little noir. "Follow the thread" energy — not
  fear-mongering. The hero is *understanding*, not the malware.
- **Audience:** Security-curious general viewers, students, blue-teamers.

## Visual language

- Dark UI, monospace type, the Cybervoid purple-orb motif from the platform.
- Real-ish terminals and browser windows, but **everything on screen is simulated or
  defanged** — no live payloads, no working commands. On-screen `REDACTED` and `[.]`
  defanging is part of the aesthetic and the ethics.
- Recurring visual metaphor: **the cache as a locker / suitcase** the browser fills without
  reading what's inside.

## Structure (three acts = three chapters of the book)

| Act | Book basis | Beat |
|-----|-----------|------|
| **Act I — The Trap** | Ch.1 §1.1–1.3 | The fake CAPTCHA; the quiet cache write; the "paste this to continue." |
| **Act II — The Staircase** | Ch.1 §1.4 + Ch.2 | Carve out of cache → batch → PowerShell → in-memory loader → stealer. How caching is abused, per browser. |
| **Act III — The Ecosystem** | Ch.3 | 2023 research → 2025 EXIF evolution → 2026 DOUBLECUP service. Why trusted things make the best hiding places. |
| **Coda — The Defenders** | App. B | It's quiet on the way in, loud on the way out. What to watch for. One rule that breaks the chain. |

## Through-line and thesis

> **Attackers hide inside the normal.** The cache exists to make the web fast; the image
> exists to be harmless; the click exists as trust; the blockchain exists to be open. Each
> was turned into a hiding place. Defense means learning to notice *the normal behaving
> strangely.*

## The "one rule" payoff (the takeaway the film builds to)

*No legitimate website will ever ask you to press Win+R and paste a command to "verify" or
"fix" something.* That single habit defeats the manual step the entire chain depends on.

## Credits & ethics card (must appear)

- Credit **John Hammond** for the origin investigation; **SensePost / Aurelien Chalot** for
  naming the technique; **MalwareTech**, **SOCRadar**, and the analyst community.
- On-screen ethics note: *"All commands and indicators shown are defanged and simulated for
  education. Nothing in this film is a working attack."*

## Deliverables

- `script-episode-01.md` — full narration + on-screen text.
- `shot-list.md` — scene-by-scene visuals, incl. lab-safe capture specs.
- Diagrams exported from the book's ASCII chain art.

# Chapter 1 — The Infected Cache

> Source: **John Hammond**, *"My Browser Cache Got Infected"* — YouTube `@_JohnHammond`
> (`youtu.be/oJHOlNTH7lY`). This chapter reconstructs the investigation as a narrative
> from the video's analysis and corroborating public reporting. Indicators are defanged.

---

## 1.1 The scene

It starts the way most of these do: an ordinary-looking web page. A visitor lands on a
site — often a legitimate one that has been **compromised** — and is met with a familiar
ritual of the modern web: *"Verify you are human."* A Cloudflare-style Turnstile box, a
spinning checkmark, the small friction we've all been trained to click through.

That training is the whole point. The prompt is a **lure**, a social-engineering pattern
the industry calls **ClickFix**: convince the human to *do a small manual step* so that
the malicious action is performed **by the user's own hands**, not by an exploit. No
memory-corruption bug, no drive-by. Just a person following instructions.

## 1.2 The sleight of hand

While the visitor reads the fake prompt, the page does something quietly clever. It
serves its **next-stage payload disguised as an image** and lets the browser do what
browsers do: **cache it to disk.** The server picks which browser you're on from your
**User-Agent** (Firefox, Chrome, or Brave) so it can tailor where the file lands and how
it will be retrieved.

Nothing about this looks alarming. Caching an image is the most normal thing a browser
can do. But the "image" is not an image — it's the malware's next stage, now sitting on
disk under a random, extension-less filename, having never announced itself as an
executable.

This is the trick the whole saga is named for: **browser cache smuggling.** (The
technique's mechanics get their own chapter — see [Chapter 2](chapter-02-cache-smuggling.md).)

## 1.3 The "fix"

Now the lure asks for the manual step. In the ClickFix pattern the page tells the victim
something like: *"Verification failed — to continue, press `Win+R`, paste this, and hit
Enter."* The victim copies a one-liner into the Windows **Run** dialog.

Here is the elegant, nasty part: the pasted command does **not** download anything. It
**reaches into the browser cache** — the file that was just quietly written while the
victim read the prompt — and **pulls the payload back out.** To a network monitor there's
no fresh malicious download at the moment of execution; the bytes were delivered earlier,
wrapped as a cached "image." The download cradle *is the browser itself.*

> **Why it works on defenders too:** many detections watch for a script that fetches a
> remote payload. Here the fetch already happened, invisibly, as a cache write. The
> execution step only touches local files.

## 1.4 Down the staircase

From the one-liner, Hammond's analysis walks the payload down a staircase of stages, each
one peeling back to reveal the next:

1. **Obfuscated batch script** — the thing carved out of the cache. Heavily mangled to
   resist a quick read.
2. **PowerShell stages** — the batch hands off to PowerShell, which reaches out to
   **lookalike domains** and **disguised IP addresses** for further stages.
3. **A fake Cloudflare challenge — rendered by PowerShell.** A striking detail: the
   attacker recreates the "are you human" experience *from within the script* to keep the
   victim calm and engaged while the real work happens.
4. **Base64-encoded ZIP** containing an **inline C# shellcode loader** — code compiled/run
   in memory so little touches disk as a recognizable executable.
5. **The infostealer** — the final stage. It does what stealers do: harvests **browser
   cookies and history**, and exfiltrates them. The browser that smuggled the malware in
   becomes the very thing that's looted.

```
 fake CAPTCHA (ClickFix lure)
        │  writes disguised payload to browser cache
        ▼
 victim pastes one-liner  ──►  carves payload OUT of cache
        ▼
 obfuscated .bat  ──►  PowerShell stages  ──►  lookalike domains / disguised IPs
        ▼
 fake PowerShell-rendered Cloudflare form  (keeps victim calm)
        ▼
 base64 ZIP  ──►  inline C# shellcode loader  (in-memory)
        ▼
 infostealer  ──►  exfiltrates cookies + history
```

## 1.5 Why this investigation matters

Hammond's walkthrough is valuable not because the malware is exotic — stealers are a dime
a dozen — but because it makes visible a **delivery innovation**: turning a universal,
trusted browser behavior (caching) into a stealthy download cradle, then getting the
*victim* to complete the chain by hand. It defeats assumptions baked into a lot of
tooling:

- "Malware has to download its payload at run time." → Not here; it was pre-staged in cache.
- "Executables look like executables on disk." → Not here; it's a cached, extension-less blob.
- "A human won't run a strange command." → ClickFix is engineered precisely to make them.

## 1.6 What we carry forward

The video gives us the **human-guided map** of one real chain. The next chapters formalize
it:

- **[Chapter 2](chapter-02-cache-smuggling.md)** — how cache smuggling actually works on
  disk, per browser, with defanged mechanics.
- **[Chapter 3](chapter-03-the-ecosystem.md)** — where this came from and who turned it
  into a paid service.
- **[Appendix A](appendix-a-artifacts.md)** — defanged artifacts and cache paths.
- **[Appendix B](appendix-b-detection.md)** — how to catch it.

> **A note on the lure's costume.** This chapter tells the story in its widely-seen
> **ClickFix / fake-Cloudflare** form. The file-level artifacts Hammond dissects match the
> **FileFix / Fortinet VPN compliance** variant documented by Expel — same cache-smuggling
> engine, different social-engineering paint. The specific files (the lure page, the
> disguised `image/jpeg` ZIP, the carve-and-run one-liner with markers `bTgQcBpv` /
> `mX6o0lBw`, the `ComplianceChecker.zip` runner) are catalogued in
> **[Appendix C — The Files, Documented](appendix-c-the-files.md)**.

> **Researcher credit:** The investigation narrated here is John Hammond's. This chapter
> is a study and retelling for defensive education, not a transcript. Watch the original.

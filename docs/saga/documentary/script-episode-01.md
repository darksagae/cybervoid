# Script — Episode 1: "The Infected Cache"

*Runtime target: ~13 min. Format: NARRATOR (VO) + ON-SCREEN text + B-ROLL notes.*
*Ethics: every terminal/browser shown is **simulated or defanged.** No working commands.*

---

### COLD OPEN  (0:00–0:45)

**B-ROLL:** Slow push into a browser window. A "Verify you are human" checkbox pulses.

**NARRATOR (VO):**
> You've seen this box a thousand times. Click it, and you're human. Click it, and the web
> lets you through. It's the smallest act of trust on the internet.
>
> This is a story about what happens when that trust is the whole attack.

**ON-SCREEN (title card):** *THE INFECTED CACHE* — Cybervoid Saga, Part I
**Ethics card (small, lower third):** *All indicators shown are defanged & simulated for education.*

---

### ACT I — THE TRAP  (0:45–4:30)

**B-ROLL:** An ordinary website loads. Everything looks fine.

**NARRATOR:**
> Our story opens with an investigation by a malware researcher named **John Hammond**. A
> website — often a legitimate one that's been quietly compromised — greets its visitor with
> a familiar prompt. *Verify you're human.* A Cloudflare-style box. Nothing unusual.
>
> But while you read it, the page is already working.

**ANIMATION:** The "cache-as-locker" metaphor. The browser opens a locker labeled CACHE and
files away an item marked with a small image icon.

**NARRATOR:**
> Web browsers keep a **cache** — a stash of files saved to your disk so pages load faster
> next time. Images, mostly. Harmless. So when this page offers the browser an "image," the
> browser does the natural thing. It saves it.
>
> Except it isn't an image. It's the next stage of the malware — now sitting on your disk,
> dressed as a picture, with no obvious name and no obvious extension.

**ON-SCREEN:** `Content-Type: image/jpeg`  →  *(bytes say: not an image)*

**NARRATOR:**
> The technique has a name: **cache smuggling.** The browser's suitcase has been packed —
> and the browser never looked inside.

**B-ROLL:** The fake prompt now says verification "failed," and shows steps: press Win+R,
paste, Enter.

**NARRATOR:**
> Then comes the ask. *To continue, press Windows-R, paste this, and hit Enter.* Security
> people call this pattern **ClickFix** — because it asks *you* to fix a problem that was
> never real.
>
> Here's the twist that makes it elegant, and awful: the command you paste doesn't download
> anything. It reaches into the cache — into the file the browser already saved — and pulls
> the malware back out. The delivery happened minutes ago, disguised as a picture. This step
> just... opens the locker.

**ON-SCREEN (defanged):** `powershell … reads %LOCALAPPDATA%\…\Cache_Data\… ` `# REDACTED`

---

### ACT II — THE STAIRCASE  (4:30–8:30)

**ANIMATION:** A descending staircase; each step lights up as the narrator names it.

**NARRATOR:**
> From that one pasted line, John Hammond walks the payload down a staircase. Each step
> reveals the next.
>
> **One:** an obfuscated batch script — deliberately scrambled to slow you down.
> **Two:** PowerShell, reaching out to lookalike domains and disguised addresses for more.
> **Three** — and this one's almost theatrical — the script *redraws the fake Cloudflare
> box itself*, in PowerShell, just to keep you calm while it works.
> **Four:** a base64-wrapped ZIP hiding a C# loader that runs in memory, so little touches
> the disk as anything you'd recognize.
> **Five:** the finale — an **infostealer**. It reads your browser's cookies and history and
> sends them away.

**B-ROLL:** Cookie jar graphic being emptied.

**NARRATOR:**
> The browser smuggled the malware in. And then the browser got robbed.

**INTERSTITIAL — "How the suitcase works" (6:30–8:30):**

**ANIMATION:** Split screen — Firefox vs. Chrome cache folders.

**NARRATOR:**
> Why does this work? Because a browser decides how to treat a file by the **label** the
> server puts on it — not by what's actually inside. Call it an image, and it's cached like
> an image.
>
> Firefox tucks each cached file into a folder and — helpfully for the attacker — keeps the
> web headers right next to it, so they can tag their file and find it again. Chrome packs
> everything into a binary database, so the attacker wraps the payload in markers and carves
> it back out.
>
> Two designs, same weakness: **the cache trusts the label.**

**ON-SCREEN (paths, defanged):**
`…\Firefox\Profiles\<p>\cache2\entries\`  ·  `…\Chrome\User Data\Default\Cache\Cache_Data\`

---

### ACT III — THE ECOSYSTEM  (8:30–11:30)

**ANIMATION:** A timeline: 2023 → 2025 → 2026.

**NARRATOR:**
> This didn't come from nowhere. In **2023**, researchers at **SensePost** named cache
> smuggling and showed it working — a proof of concept, a curiosity.
>
> By **2025**, it evolved. Instead of a fake image, the payload started riding *inside a real
> one* — hidden in the metadata a photo viewer ignores. **MalwareTech** documented it.
>
> And by **2026**, it had a storefront. A service called **DOUBLECUP** rented the whole
> operation out: it hosts the poisoned images, manages the keys, rebuilds the payloads —
> so a criminal with no skill can just bolt it onto a fake CAPTCHA page impersonating brands
> like NetSuite or HubSpot.

**ON-SCREEN:** *DOUBLECUP — loader-as-a-service — cached PNGs — CountLoader + DeviceManager*

**NARRATOR:**
> The payloads got nastier — a stealer chasing crypto wallets and Signal; a Python remote-
> access trojan that hides its command server *on a public blockchain*, where no one can
> take it down.
>
> Notice the pattern. The cache — built to make the web fast. The image — built to be
> harmless. The click — built on trust. The blockchain — built to be open. Every single one
> was turned into a hiding place.

---

### CODA — THE DEFENDERS  (11:30–13:00)

**B-ROLL:** A SOC analyst's screen; a single alert lights up.

**NARRATOR:**
> So how do you catch something built to look normal? You watch for **normal behaving
> strangely.**
>
> Cache smuggling is quiet on the way in — but **loud on the way out.** You might miss the
> disguised image landing. But you *can* see a File Explorer window suddenly spawn PowerShell
> that reads the browser cache. And you can always see a stealer raid the cookie jar and
> phone home. Watch the loud moments.

**ON-SCREEN (the rule, big):**
> **No real website ever asks you to press Win+R and paste a command to "verify" or "fix"
> anything.**

**NARRATOR:**
> That one habit breaks the whole chain. Because every clever layer we just walked through
> still needs the same final thing:
>
> It needs *you* to open the locker.

**CREDITS:**
- Origin investigation: **John Hammond** — *My Browser Cache Got Infected.*
- Technique named by **SensePost (Aurelien Chalot)**, 2023. Evolution: **MalwareTech**, 2025.
  DOUBLECUP reporting: **SOCRadar / BleepingComputer**, 2026.
- *All commands and indicators in this film are defanged and simulated for education.*
- A Cybervoid Saga production.

**FADE OUT.**

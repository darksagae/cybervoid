# Script — Episode 2: "The Marketplace"

*Runtime target: ~12 min. Format: NARRATOR (VO) + ON-SCREEN text + B-ROLL notes.*
*Based on [Chapter 4](../chapter-04-the-marketplace.md). Everything shown is simulated/defanged.*

---

### COLD OPEN  (0:00–0:50)

**B-ROLL:** A clean SaaS-style web dashboard — the kind a business runs on. It could be any
tool. A cursor hovers a "product" listing.

**NARRATOR (VO):**
> In Episode 1, one attacker hid malware in a browser's cache and talked a victim into
> opening it. Clever. Handmade. The work of someone who understood the trick.
>
> This episode is about what happens next — when the trick gets a price tag.

**ON-SCREEN (title):** *THE MARKETPLACE* — Cybervoid Saga, Part II
**Ethics card:** *All indicators shown are defanged & simulated for education.*

---

### ACT I — FROM TRICK TO PRODUCT  (0:50–3:30)

**ANIMATION:** A single lone-hacker icon multiplies into a storefront with many customers.

**NARRATOR:**
> A technique is dangerous when a researcher demonstrates it. It becomes an epidemic when
> someone turns it into something a stranger can rent.
>
> By June 2026, that's exactly what happened. A service — call it by its name, **DOUBLECUP** —
> started selling browser cache smuggling as a subscription. Malware delivery, with a
> customer-support model.

**ON-SCREEN:** *DOUBLECUP — "loader-as-a-service"*

**NARRATOR:**
> The buyer doesn't need to understand any of the clever parts. They don't manage keys.
> They don't hide payloads in images. They just take the service's code, bolt it onto a fake
> CAPTCHA page, and send people to it. The engine does the rest.

---

### ACT II — WHAT THE ENGINE DOES  (3:30–7:00)

**ANIMATION:** The service diagram from Chapter 4 — customer on the left, the rented engine
on the right, a victim flowing through the middle.

**NARRATOR:**
> Here's what you're renting. The service **hosts the poisoned images** — real, valid PNGs
> with the payload hidden inside. It **manages the sessions**, tracking each victim through
> the chain. It **hands out encryption keys**, one per victim. And it **rebuilds the payload
> automatically**, so yesterday's antivirus signature is already useless.

**ON-SCREEN (four cards):** *hosts steganographic PNGs · manages sessions · per-victim keys ·
auto-rebuilds payloads*

**NARRATOR:**
> The chain itself is Episode 1's trick, one turn more evolved. The lure impersonates
> business software people trust. The browser caches the PNG. The victim pastes the command —
> but this version doesn't hunt for a secret marker. It searches the cache **by file size**,
> and pulls the payload out with tools already built into Windows.

**B-ROLL:** A file browser sorting by size; one file highlighted.

**NARRATOR:**
> Then the nastiest touch. Before the payload will even unlock, a small dropper looks up the
> victim's **IP address** and uses it to build the decryption key. Lift that sample into a
> lab, and it simply won't open. The malware is keyed to the victim's own network.

**ON-SCREEN:** *anti-analysis: decryption key derived from the victim's IP*

---

### ACT III — THE CARGO  (7:00–9:30)

**ANIMATION:** Two crates unloaded from the engine.

**NARRATOR:**
> What gets delivered? Two things worth naming.
>
> The first, **CountLoader** — a stealer that goes straight for cryptocurrency wallets and
> Signal, and digs in with scheduled tasks.
>
> The second is stranger. A Python remote-access trojan called **DeviceManager** — and it
> hides its command server on a **blockchain**. The address it phones home to lives on a
> public, permanent ledger. There's no domain to seize, no server to take down. The instructions
> are written somewhere no one can erase.

**ON-SCREEN:** *CountLoader (stealer) · DeviceManager (Python RAT, C2 hidden on-chain)*

**NARRATOR:**
> Look at the whole picture. The delivery hides in the cache. The payload hides in an image.
> The command channel hides on a blockchain. Every layer buried inside something ordinary and
> hard to take down.

---

### ACT IV — THE LOOSE THREAD  (9:30–11:00)

**B-ROLL:** A plain server directory listing — open to the world.

**NARRATOR:**
> And yet. Every marketplace leaves a door open.
>
> In August 2026, researchers at SOCRadar found DOUBLECUP's — an **open directory**, test
> files sitting exposed on a server for anyone to see. That's the thread. That's how you pull
> an industrialized operation apart: not by out-hacking it, but by noticing the ordinary
> mistake it left behind.

---

### CODA — WHAT SCALE CHANGES  (11:00–12:00)

**B-ROLL:** The SOC screen again; more alerts than in Episode 1, but the analyst is calm.

**NARRATOR:**
> When a technique becomes a product, you're no longer facing one person's skill. You're
> facing everyone who can pay. The volume goes up. The payloads mutate faster than any
> signature.
>
> So you stop chasing the file, and you watch the **behavior** — the things the engine can't
> hide. A browser's cache being read by something that isn't the browser. A built-in Windows
> tool carving data it has no reason to touch. And underneath all of it, the one step no
> subscription can remove:

**ON-SCREEN (big):**
> **It still needs a human to paste the command.**

**NARRATOR:**
> Industrialize everything else, and that door is still there. Which is exactly where Episode 3
> begins — with the defenders who learned to guard it.

**CREDITS:**
- Based on SOCRadar's research (reported via BleepingComputer), 2026.
- *All indicators defanged and simulated for education.* A Cybervoid Saga production.

**FADE OUT.**

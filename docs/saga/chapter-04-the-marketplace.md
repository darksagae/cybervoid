# Chapter 4 — The Marketplace

> *Episode 2 of the saga.* Where Chapter 1 followed a single infection, this chapter follows
> the **business** that sells it. Primary sources: SOCRadar (via BleepingComputer) on
> **DOUBLECUP**, 2026; corroborated by the technique history in
> [Chapter 3](chapter-03-the-ecosystem.md). Defanged throughout.

---

## 4.1 From trick to product

A technique is dangerous when a researcher demonstrates it. It becomes an *epidemic* when
someone turns it into a product a stranger can rent. That is the story of **DOUBLECUP**: the
moment browser cache smuggling stopped being clever tradecraft and became **loader-as-a-
service** — malware delivery with a customer support model.

By early **June 2026**, DOUBLECUP was operating as managed criminal infrastructure. A
customer — who need not understand cache smuggling, steganography, or key management at all —
just bolts DOUBLECUP's code onto a fake CAPTCHA page and points victims at it. The service
does the hard parts.

## 4.2 What the service actually runs for you

Per SOCRadar's research, DOUBLECUP "handles much of the infrastructure required to conduct
the attacks." Concretely, the platform:

- **Hosts the steganographic PNG images** — the smuggled payloads, carried inside real,
  valid images (the 2025 EXIF evolution from [Chapter 3](chapter-03-the-ecosystem.md)).
- **Manages session and signal endpoints** — the plumbing that tracks victims and stages.
- **Provides encryption keys** — so payloads are encrypted per-victim.
- **Automatically rebuilds payloads** — regenerates samples to stay ahead of signatures.

The customer supplies only the lure and the traffic. Everything technical is a service call.

```
   CUSTOMER                         DOUBLECUP  (the rented engine)
   ─────────                        ──────────────────────────────
   fake CAPTCHA site   ───────────► hosts steganographic PNGs
   (NetSuite / HubSpot themes)      manages session + signal endpoints
        │                           provides per-victim encryption keys
        │  sends victims            auto-rebuilds payloads to dodge AV
        ▼
   VICTIM  ──► caches PNG ──► ClickFix paste ──► carve by file-size ──► in-memory payload
```

## 4.3 The chain, one turn more evolved

DOUBLECUP's chain is the saga's technique, refined for scale:

1. **Lure.** Fake CAPTCHA pages **impersonating NetSuite, HubSpot**, and similar SaaS —
   brands an enterprise user trusts.
2. **Smuggle.** The browser caches a malicious **PNG** (a genuine image with the payload
   hidden inside — not a crude fake-JPEG).
3. **ClickFix.** Instructions get the victim to paste a command.
4. **Locate by size.** Rather than marker strings, the pasted command **searches the cache
   by exact file size** and extracts with living-off-the-land tools **`findstr` / `certutil`**.
5. **Keying.** A **fileless second-stage dropper** fetches the **victim's IP** and uses it to
   derive decryption keys — so a carved sample won't decrypt in an analyst's sandbox.
6. **Detonate in memory.** Final payloads run **in memory**, minimizing disk artifacts.

> **Analyst's note — the IP-derived key is an anti-analysis move.** Bind the decryption key
> to the victim's network context and a payload lifted to a lab simply won't open. It's the
> same philosophy as cache smuggling: make the malicious part depend on something *normal*.

## 4.4 The cargo

DOUBLECUP delivers two notable payloads to **Windows and macOS**:

- **CountLoader** — an infostealer that targets **cryptocurrency wallets** and **Signal
  Desktop**, and persists via **scheduled tasks** (ATT&CK T1053.005).
- **DeviceManager** — a **Python modular RAT** whose standout trait is **EtherHiding**: it
  reads its command-and-control address from a **blockchain smart contract**. There's no
  domain or IP to seize; the C2 pointer lives on a public, immutable ledger.

Together they show the endgame of the "hide in the normal" philosophy: the delivery hides in
cache, the payload hides in an image, and the *command channel hides on a blockchain.*

## 4.5 The loose thread

Every marketplace leaves a door open. DOUBLECUP's was an **open directory** — exposed test
files at `213.139.77[.]109:9090`, which **SOCRadar found in August 2026**. It's the small,
human mistake that lets defenders pull on a thread and unravel the operation: a reminder that
even industrialized crime runs on misconfigured servers.

## 4.6 Why the marketplace matters to defenders

1. **Scale changes the threat model.** You are no longer facing one actor's skill; you're
   facing a technique **democratized** to everyone who can pay. Volume and variety go up.
2. **Signatures age faster.** Auto-rebuilt, per-victim-encrypted payloads defeat static
   hashes. **Behavioral** detection (a shell reading `Cache_Data`, `certutil` carving,
   `explorer`→PowerShell) is the durable answer — see [Appendix B](appendix-b-detection.md).
3. **The human step is still mandatory.** However industrialized the back end, the chain
   still needs the victim to paste. **The one rule still ends it:** no site asks you to press
   `Win+R` (or paste into Explorer) to "verify" or "fix" anything.
4. **Hunt the loose threads.** Open directories, reused endpoints, and blockchain-RPC calls
   from odd processes (EtherHiding) are the marketplace's fingerprints.

## 4.7 Where this sits in the saga

- Chapter 1 was **one infection**, human-guided.
- Chapters 2–3 were the **technique and its history**.
- Chapter 4 is the **business** that scaled it.

The arc's lesson is consistent from PoC to product: **trusted, ubiquitous mechanisms make
the best hiding places — so detection must watch trusted things behaving strangely.**

Documentary note: this chapter is the basis for **Episode 2 — "The Marketplace."** The
[treatment](documentary/treatment.md) Act III already seeds it; a dedicated Ep.2 script can
follow the 4.2 service diagram and the 4.5 open-directory beat.

*Sources:* [sources.md](sources.md) (BleepingComputer/SOCRadar on DOUBLECUP; technique
lineage from SensePost and MalwareTech).

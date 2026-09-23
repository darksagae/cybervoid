# Appendix B — Detection & Hunting

> Turns the openings from [Chapter 2 §2.5](chapter-02-cache-smuggling.md) and the artifacts
> in [Appendix A](appendix-a-artifacts.md) into practical detection logic. Pseudo-rules are
> written to be **adapted**, not pasted blind — tune paths, exclusions, and thresholds to
> your environment. Mapped to MITRE ATT&CK where it helps.

---

## B.1 The four detection surfaces

```
  ┌── NETWORK ───────────────────────────────────────────────┐
  │  image/* response whose body is a PE/ZIP  (T1027, T1105)  │
  ├── DISK / FORENSICS ──────────────────────────────────────┤
  │  cache blob with type/magic mismatch; odd custom headers  │
  ├── PROCESS / EDR ─────────────────────────────────────────┤
  │  explorer→shell w/ cache path; non-browser reads Cache;   │
  │  certutil/findstr over cache  (T1204, T1059, T1140)       │
  └── OUTCOME ───────────────────────────────────────────────┘
     infostealer reads cookie/login stores → egress  (T1539, T1555)
```

## B.2 Network — the type/content mismatch

**Idea:** a response labeled `image/*` should start with image magic bytes. Flag when it
doesn't.

```
# Proxy / IDS pseudo-rule
IF http.response.header["Content-Type"] MATCHES "image/(jpeg|png|gif|webp)"
   AND http.response.body[0:4] IN { "MZ..", "PK\x03\x04", "MSCF" }   # PE / ZIP / CAB
THEN alert "Cache-smuggling: image Content-Type with executable/archive body"
```
Suricata-style file-magic rules (`filemagic`) or a Zeek `file_analysis` script keyed on
`mime_type` vs. observed magic implement this well.

**ATT&CK:** T1027 (Obfuscated/Disguised Files), T1105 (Ingress Tool Transfer).

## B.3 Disk / forensic sweep

**Chromium** — hunt `Cache_Data` for `f_######` entries whose stored Content-Type is image
but whose first bytes are `MZ`/`PK`:

```
# Analyst pseudo-logic (run on a forensic image, not blindly in prod)
FOR each file in %LOCALAPPDATA%\**\Cache\Cache_Data\f_*:
    if header_says_image(file) and magic_bytes(file) in (PE, ZIP): flag(file)
```

**Firefox** — grep `cache2\entries\` for suspicious custom headers next to image types:

```
findstr /S /I /C:"Content-Type: image" /C:"Tag:"  "%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*\cache2\entries\*"
# review any entry where an odd custom header co-occurs with an image type but non-image body
```

**ATT&CK:** T1074 (Data Staged), forensic corroboration of T1027.

## B.4 Process / EDR — the loud moments

These are the highest-fidelity signals; smuggling is quiet, but **retrieval and execution
are not.**

**R1 — explorer spawns a shell referencing the cache (ClickFix hand-off):**
```
parent_image ENDS_WITH "\explorer.exe"
AND child_image IN ("\cmd.exe","\powershell.exe","\pwsh.exe","\mshta.exe","\wscript.exe")
AND child_cmdline CONTAINS_ANY ("Cache_Data","cache2\\entries","\\Cache\\")
=> HIGH  # ClickFix Run-box execution referencing browser cache
```
**ATT&CK:** T1204.002 (User Execution: Malicious File), T1059.001/003.

**R2 — non-browser process reads the cache directory:**
```
file_read_path CONTAINS_ANY ("Cache_Data","cache2\\entries")
AND process_image NOT_IN (known_browser_binaries)
=> MEDIUM-HIGH
```

**R3 — LOLBins carving the cache:**
```
process_image ENDS_WITH_ANY ("\certutil.exe","\findstr.exe")
AND cmdline CONTAINS_ANY ("Cache_Data","cache2\\entries")
=> HIGH  # certutil -decode / findstr marker-carve over cache
```
**ATT&CK:** T1140 (Deobfuscate/Decode Files), T1059.

**R4 — extension-less DLL via rundll32:**
```
process_image ENDS_WITH "\rundll32.exe"
AND cmdline MATCHES a path with NO ".dll" extension before the comma-export
=> MEDIUM
```

## B.5 Outcome — catch the stealer even if you missed the delivery

If delivery slipped through, the **infostealer finale** is still catchable:

```
# Bulk credential-store access followed by egress
process reads MANY of:
   ...\Chrome\User Data\**\Network\Cookies
   ...\Chrome\User Data\**\Login Data
   ...\Firefox\Profiles\**\cookies.sqlite
within a short window, by a NON-browser process,
THEN outbound connection to a low-reputation host
=> HIGH  # infostealer collection + exfil
```
**ATT&CK:** T1539 (Steal Web Session Cookie), T1555.003 (Credentials from Web Browsers),
T1041 (Exfiltration Over C2).

## B.6 Hunt hypotheses (for threat hunters)

1. *"An image was really a program."* Sweep proxy logs for `image/*` responses with
   PE/ZIP magic. Pivot on serving hosts.
2. *"A human ran the malware for the attacker."* Hunt `explorer.exe` → shell with a cache
   path in the command line across the fleet.
3. *"A LOLBin touched the cache."* `certutil`/`findstr` with `Cache_Data`/`cache2` in args.
4. *"The cache holds a stranger."* On triage images, diff cache Content-Type vs. magic bytes.
5. *"C2 is hiding on-chain."* For DeviceManager-style RATs, watch for processes querying
   public blockchain RPC endpoints with no business reason (EtherHiding).

## B.7 Hardening & user-side mitigations

- **Break the ClickFix muscle memory.** Train users: *no legitimate site asks you to press
  `Win+R` and paste a command to "verify" or "fix" anything.* This single message defeats
  the manual step the whole chain depends on.
- **Constrain the Run/execution path.** Where feasible, restrict `Win+R`, apply
  **application control** (WDAC/AppLocker) so carved payloads can't execute, and monitor
  `explorer.exe` child processes.
- **Constrain LOLBins.** Alert on / restrict `certutil`, `mshta`, `findstr` in scripting
  contexts.
- **Proxy content inspection.** Enforce type/magic agreement on cached content where your
  proxy supports it.
- **Browser hygiene.** Site isolation, careful extension policy, and clearing caches reduce
  the staging surface (though the technique re-seeds on each visit).

---

### One-line takeaway for the SOC

> **Cache smuggling is quiet on the way in and loud on the way out.** You may not see the
> disguised image land, but you *can* see a person's Explorer window spawn PowerShell that
> reads the browser cache — and you can always see a stealer raid the cookie jar. Watch the
> loud moments.

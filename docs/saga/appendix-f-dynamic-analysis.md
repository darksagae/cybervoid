# Appendix F — Dynamic Analysis (from Public Sandbox & Vendor Reports)

> **How the live payload behaves — documented from free, public detonation/analysis reports,
> not from running it here.** Executing the real chain (`stage2.ps1` → `irm <C2>; iex`) means
> contacting attacker C2 and running unknown code; that belongs in a purpose-built, network-
> isolated malware sandbox, not this environment. Instead, this appendix consolidates the
> **observed runtime behavior** that professional analysts and automated sandboxes already
> captured. Sources in [sources.md](sources.md); indicators defanged.

---

## F.0 Why this appendix exists (and how it was made)

The user asked to "run the real live payload in a protected sandbox." Detonation is legitimate
malware analysis — but only in an isolated rig with simulated internet and snapshots (see
[§F.4](#f4-how-a-real-detonation-lab-is-built)). Rather than detonate in a non-isolated cloud
container, we use the **free public record**: this exact family has been detonated and
dissected by Expel (Marcus Hutchins), Push Security, Palo Alto **Unit 42**, and automated
sandboxes (**ANY.RUN**). That gives us real dynamic behavior at zero risk.

## F.1 Observed execution flow (runtime)

Reconstructed from the public reports, matching our static analysis in
[Appendix C](appendix-c-the-files.md) (FileFix/Fortinet) and [Appendix E](appendix-e-frames.md)
(ClickFix/Cloudflare):

```
 1. PAGE LOAD      JS makes the browser fetch a file typed image/jpeg → cached to disk
                   (pre-positioned BEFORE any command runs)
 2. LURE           victim pastes the "fix" (Win+R run box  OR  Explorer address bar/FileFix)
 3. HIDDEN LAUNCH  command runs via conhost.exe in HEADLESS mode (window hidden)
 4. CARVE          locate the cached payload — by exact SIZE (Cloudflare variant, %~zf==17635)
                   or by MARKER strings (Fortinet variant, bTgQcBpv…mX6o0lBw) — copy it out
 5. STAGE 2        PowerShell runs the carved payload:
                     • Cloudflare variant → irm to velcap C2 + obfuscated iex; draws fake CF form
                     • Fortinet variant   → Expand-Archive → FortiClientComplianceChecker.exe
 6. PAYLOAD        infostealer executes (see F.3); persistence via scheduled task
 7. EXFIL          browser cookies/creds + host data sent to C2
```

**Key runtime tell (all variants):** *no file is downloaded at execution time* — the bytes
were cached during step 1. As Marcus Hutchins put it: *"Neither the webpage nor the PowerShell
script explicitly download any files… tools scanning downloaded files or looking for PowerShell
scripts performing web requests wouldn't detect this behavior."*

## F.2 Observed host behavior (process / file / network)

| Surface | Observed behavior |
|---------|-------------------|
| **Process** | `explorer.exe` → `conhost.exe --headless` → `powershell.exe` (hidden window); non-browser process reading browser cache |
| **File** | new folder + carved artifact under `%LOCALAPPDATA%` (e.g. `\FortiClient\compliance\`) or `%TEMP%\t.bat`; `ComplianceChecker.zip` / `.exe` written and run |
| **Cache read** | `Cache_Data` / `cache2\entries\` accessed by something that isn't the browser |
| **Network** | **none at carve time**; then stage-2 PowerShell beacons to lookalike IPs (Cloudflare variant: `45.39.216[.]46/velcap3b|3d`, fallback `45.25.77[.]550`); final stealer exfil |
| **Persistence** | scheduled task (CountLoader/DOUBLECUP family) |

These map to the detection rules in [Appendix B](appendix-b-detection.md) and the ATT&CK IDs in
[Appendix D](appendix-d-attack-mapping.md).

## F.3 Final payloads seen in the wild

Tracked by the public reports across this technique's campaigns:

| Payload | Platform | Notes |
|---------|----------|-------|
| **DeerStealer** | Windows | infostealer (Unit 42's tracked FileFix campaign) |
| **Odyssey** | macOS | infostealer (same campaign) |
| **CountLoader** | Windows | stealer; crypto wallets + Signal; scheduled-task persistence (DOUBLECUP) |
| **DeviceManager** | Windows | Python RAT; EtherHiding blockchain C2 (DOUBLECUP) |
| **LummaStealer** | Windows | earlier ClickFix wave (Hammond's `recaptcha-phish` lineage) |

## F.4 How a real detonation lab is built (the safe methodology)

If you *do* want to detonate this sample yourself, this is the legitimate way — and why it
can't be this container:

1. **Isolated VM, snapshotted.** A disposable Windows VM (e.g. **FLARE-VM**) on a host-only
   network, with a clean snapshot to revert to. No bridge to the real LAN/internet.
2. **Simulated internet.** A second VM (**REMnux**) running **INetSim** or **FakeNet-NG** so
   the malware's C2 fetch (`irm <C2>`) is *answered by the lab*, captured, and **never leaves
   it**. This is the "protected" part — the C2 request is contained, not forwarded.
3. **Instrumentation.** Procmon, Process Hacker, Sysmon, a network capture (Wireshark), and a
   registry/file diff, all recording before you paste the command.
4. **Detonate, observe, revert.** Run the sample, collect artifacts, then roll the snapshot
   back. Never reuse the VM for anything else.
5. **Or use a hosted sandbox.** **ANY.RUN**, **Joe Sandbox**, **Hybrid Analysis**, and
   **VirusTotal** run this for you in their own isolated infrastructure — free tiers exist —
   and hand back the behavior report. That's what F.1–F.3 draw on.

> The difference that matters: in (1)–(2) the C2 request hits a **fake internet inside the
> lab**; in this cloud container it would hit the **real C2**. That's the line this project
> won't cross here — and doesn't need to, because the behavior is already on record.

## F.5 Attribution & timeline

| When | Who | Contribution |
|------|-----|--------------|
| Oct 2025 | **P4nd3m1cb0y** | first discovery of the FileFix + cache-smuggling variant |
| 2025 | **Expel — Marcus Hutchins** | detailed technical breakdown (Appendix C basis) |
| 2025–26 | **Palo Alto Unit 42** | "IUAM ClickFix Generator" toolkit; DeerStealer/Odyssey tracking |
| 2026 | **SOCRadar / BleepingComputer** | DOUBLECUP loader-as-a-service (Chapter 4) |
| — | **John Hammond** | the video walkthrough this saga opens on (Appendix E) |

---

*Bottom line:* the live payload's behavior is **fully documented here from public detonations**
— no local execution required, and none performed. To reproduce it first-hand, use §F.4's
isolated lab or a hosted sandbox, never a general-purpose environment.

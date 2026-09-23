# Sources

Full bibliography for **The Cybervoid Saga**. Primary sources (the original researcher's
own write-up or video) are marked ★. Access dates reflect the research sessions logged in
[research-log.md](research-log.md).

---

## Origin video (the saga's opening)

- ★ **John Hammond — "My Browser Cache Got Infected."** YouTube, channel `@_JohnHammond`.
  `https://youtu.be/oJHOlNTH7lY`
  Metadata confirmed via YouTube oEmbed and noembed (title + author). The human-guided
  walkthrough of the live ClickFix + cache-smuggling chain that anchors Chapter 1.

## The technique — primary research

- ★ **Aurelien Chalot (SensePost) — "Browsers' cache smuggling."** 2023-07-10.
  `https://sensepost.com/blog/2023/browsers-cache-smuggling/`
  Original naming and PoC: `image/jpeg` mislabeling, `<img>`-forced caching, per-browser
  disk locations, header-tag / marker-carve retrieval, `rundll32` extension-less exec.

- ★ **MalwareTech — "Passively Downloading Malware Payloads Via Image Caching."** 2025-10.
  `https://malwaretech.com/2025/10/exif-smuggling.html`
  The EXIF/steganographic evolution — payload carried inside a genuinely valid image.

## Campaigns & criminal services

- **BleepingComputer — "New DOUBLECUP ClickFix service hides malware in browser cache
  images."** 2026.
  `https://www.bleepingcomputer.com/news/security/new-doublecup-clickfix-service-hides-malware-in-browser-cache-images/`
  Loader-as-a-service; cached PNGs; CountLoader + DeviceManager; size-based carve with
  `findstr`/`certutil`; EtherHiding C2; SOCRadar open-directory discovery
  (`213.139.77[.]109:9090`, Aug 2026).

- **SOCRadar** — original research behind the DOUBLECUP reporting (via BleepingComputer).

## Analyst write-ups (detection & framing)

- **CyberMaxx — "Cache Smuggling: The Interesting Download Cradle Provided by Your Internet
  Browser."**
  `https://www.cybermaxx.com/resources/cache-smuggling-the-interesting-download-cradle-provided-by-your-internet-browser/`

- **Arete — "New Browser Cache Smuggling Technique / Threat Analysis."**
  `https://areteir.com/article/browser-cache-smuggling-threat-analysis/`

- **daily.dev discussion — "My Browser Cache Got Infected."**
  `https://daily.dev/posts/my-browser-cache-got-infected-tfmxljj7l`

## Background & related

- **Wikipedia — Stegomalware.** `https://en.wikipedia.org/wiki/Stegomalware`
- **arXiv — "Bypassing antivirus detection: old-school malware, new tricks."**
  `https://arxiv.org/pdf/2305.04149`
- **John Hammond — professional profile.** `https://johnhammond.llc/` ·
  `https://www.linkedin.com/in/johnhammond010/`

## MITRE ATT&CK techniques referenced

| ID | Name |
|----|------|
| T1027 | Obfuscated Files or Information |
| T1105 | Ingress Tool Transfer |
| T1204.002 | User Execution: Malicious File |
| T1059.001/003 | Command & Scripting Interpreter (PowerShell / cmd) |
| T1140 | Deobfuscate/Decode Files or Information |
| T1074 | Data Staged |
| T1539 | Steal Web Session Cookie |
| T1555.003 | Credentials from Web Browsers |
| T1041 | Exfiltration Over C2 Channel |

---

*Citation note:* This book paraphrases and studies the sources above for defensive
education. Where a technique is described, the intent is recognition and detection, not
reproduction. Please support the original researchers by reading/watching their work
directly.

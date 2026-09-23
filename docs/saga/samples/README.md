# Samples — Password-Protected

Extracted payload code from the saga is stored here **inside a password-protected ZIP**, so
it cannot be opened, indexed, or run by accident. This is standard malware-analysis hygiene:
gate the sample, and document it in the open.

## `payload-void.zip`

| | |
|---|---|
| **Password** | `void` |
| **Contents** | `payload.txt` (extracted lure + extractor + stage-2 beacon + decoy), `READ_ME_FIRST.txt` |
| **Campaign** | ClickFix / fake-Cloudflare on compromised `smilesofboca` |
| **Full analysis** | [Appendix E](../appendix-e-frames.md) · detection: [Appendix B](../appendix-b-detection.md) |

**Open it:**
```bash
unzip -P void docs/saga/samples/payload-void.zip -d ./out
# or double-click and enter the password: void
```

## Two layers of safety

1. **Password gate (`void`)** — prevents *accidental* access/execution and keeps the raw
   text out of casual browsing and search indexing.
2. **Defanged + neutralized content** — even once opened, every C2 host is written with `[.]`
   (won't resolve) and every execution step is disabled (`REM` / `<-- REDACTED`). The ZIP
   password is intentionally weak, so this second layer is the real protection: it is a
   **record, not a runnable tool.**

> ⚠️ For defensive study and education only. Do not re-arm, re-host, contact the C2s, or run
> any of the contents. The C2 IPs were transcribed by eye from video frames — verify before
> any operational use.

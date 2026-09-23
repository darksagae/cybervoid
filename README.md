# CYBERVOID

**A security-research platform and knowledge base** — a purple-orb desktop app for exploring
offensive/defensive tooling, plus **The Cybervoid Saga**, a documented book of cyber-research.

---

## 📖 The Cybervoid Saga

A living **book of records** — a defensive-security investigation documented as a saga, from
a single real-world infection out to the criminal marketplace that industrialized it. It
begins with researcher **John Hammond's** *"My Browser Cache Got Infected"* and follows the
**browser cache smuggling** technique through its history, its files, and how defenders hunt
it — all defanged for safe study — and ends in a **documentary** treatment.

**➡ Start here: [`docs/saga/`](docs/saga/README.md)**

| What | Where |
|------|-------|
| The book (preface + how the research was made) | [`docs/saga/README.md`](docs/saga/README.md) · [`research-log.md`](docs/saga/research-log.md) |
| Chapters 1–5 | [The Infected Cache](docs/saga/chapter-01-the-infected-cache.md) · [Cache Smuggling](docs/saga/chapter-02-cache-smuggling.md) · [The Ecosystem](docs/saga/chapter-03-the-ecosystem.md) · [The Marketplace](docs/saga/chapter-04-the-marketplace.md) · [The Defense](docs/saga/chapter-05-the-defense.md) |
| Appendices | [A Artifacts](docs/saga/appendix-a-artifacts.md) · [B Detection](docs/saga/appendix-b-detection.md) · [C The Files](docs/saga/appendix-c-the-files.md) · [D ATT&CK](docs/saga/appendix-d-attack-mapping.md) · [E Frame-by-Frame](docs/saga/appendix-e-frames.md) |
| Runnable, **benign** lab | [`docs/saga/lab/`](docs/saga/lab/README.md) |
| Captured evidence (real screenshots) | [`docs/saga/screenshots/`](docs/saga/screenshots/) |
| ATT&CK Navigator layer | [`attack-navigator-layer.json`](docs/saga/attack-navigator-layer.json) |
| Documentary (treatment · script · shot list · pitch deck) | [`docs/saga/documentary/`](docs/saga/documentary/) |

> **Ethics:** every indicator and command in the saga is **defanged and simulated** for
> education. The lab contains no malware; the "payload" is a text file that says so.

---

## 🖥 The platform

CYBERVOID is a desktop security-research UI (Ursina/Python) with a categorized tool
launcher, an execution engine, and an AI chat assistant.

| File | Role |
|------|------|
| `orb.py` | The main app — the purple-orb UI and tool launcher |
| `tools_data.py` | Categorized catalog of security tools (recon, vuln, web, etc.) |
| `exec_engine.cpp` / `exec_engine` | Native execution engine |
| `ai_chat.py` | AI chat assistant integration |
| `database.py` / `buitesuite.db` | Local state |
| `frontend/` | Next.js companion frontend |

### Run

```bash
make               # build the native exec engine
python3 orb.py     # launch the desktop app
```

Requires Python 3 with [Ursina](https://www.ursinaengine.org/); see `frontend/` for the web
companion.

---

## Repository layout

```
cybervoid/
├── orb.py, tools_data.py, ai_chat.py, database.py   # the platform
├── exec_engine.cpp, Makefile                        # native engine
├── frontend/                                        # Next.js companion
└── docs/saga/                                        # The Cybervoid Saga (research book)
```

## Scope & intent

This project is for **authorized, defensive, and educational** security research. The saga
studies attacker tradecraft to teach detection and forensics; it is not an attack toolkit,
and all live indicators are neutralized.

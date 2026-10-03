# RDRS — Design Write-up

> Ransomware Detection and Response System
> A defensive cybersecurity project — rule-based detection, no machine learning

---

## 1. What was built

A defensive ransomware detector that watches file-system activity in real
time, scores suspicious behaviour, and produces incident evidence with
an explainable threat score.

**Core capabilities:**

- Real-time file monitoring (created / modified / moved / deleted)
- Shannon entropy analysis of written files
- Sliding 60-second detection window
- Weighted threat scoring: Normal (0–39) / Warning (40–69) / Critical (70–100)
- SQLite persistence: events, process snapshots, alerts, incidents
- Evidence quarantine — copies only, never touches originals
- REST API with aggregate `/dashboard` endpoint
- Live security dashboard with 8 metric panels
- JSON + CSV incident report generation
- Docker Compose deployment (Fedora / SELinux-aware)
- 41 automated tests passing, 87% code coverage

---

## 2. Design choices

### 2.1 Modular architecture

Each concern lives in its own module:

- `app/core/` — config, entropy, logging, process utilities
- `app/detectors/` — watchdog-based monitor + detection engine
- `app/database/` — SQLAlchemy models + CRUD helpers
- `app/api/` — FastAPI endpoints
- `app/dashboard/` — single-file HTML dashboard
- `app/reports/` — JSON / CSV report generator

This makes each unit independently testable and replaceable. Adding a
new detection signal requires touching `engine.py` only. Adding a new
dashboard widget requires touching `index.html` only.

### 2.2 Rule-based, not machine learning

The threat score is a **weighted sum of named signals**:

| Signal            | Weight | Fires when                                 |
|-------------------|--------|--------------------------------------------|
| rapid_encryption  | 40     | >20 files modified in 60 s                 |
| mass_rename       | 30     | >10 files renamed in 60 s                  |
| high_entropy      | 25     | average entropy > 6.5 (out of 8)           |
| cpu_spike         | 15     | latest process CPU > 60%                   |
| unknown_process   | 10     | suspect process not in whitelist           |

Weights are configurable in `config.yaml`. Score is capped at 100.

**Why this design:** a rule engine is transparent. Every point of the
score can be traced to a specific, named signal. The user does not have
to trust a model — they can read exactly why RDRS said "Critical". This
also means zero training data, zero drift, and a codebase a student can
actually reason about.

### 2.3 Simulation mode by default

`config.yaml` ships with `simulation_mode: true`. In this mode:

- Quarantine **copies** evidence files — originals are never modified
- Process termination is **logged**, never executed

This makes RDRS safe to run on a personal machine while still exercising
the full detection + response pipeline.

### 2.4 Entropy read on the renamed file

An early version read entropy when the file was created or modified. That
missed fast attacks because ransomware writes high-entropy bytes and then
renames the file in the same instant — by the time watchdog fired
`on_closed`, the source path no longer existed.

The fix: read entropy from the **destination path** on `moved` events.
The content survives the rename, so `.locked` files with ~8.0 entropy
are caught reliably.

---

## 3. How it was tested

### 3.1 Automated tests — 41 passing

Organised by module:

- `test_entropy.py` — empty / uniform / random bytes, file I/O, missing file
- `test_config.py` — YAML loading, threshold bounds
- `test_crud.py` — every CRUD function for every table
- `test_engine.py` — Normal path through the engine
- `test_engine_critical.py` — burst events drive score to Warning / Critical
- `test_api.py` — all 7 REST endpoints via FastAPI TestClient
- `test_process.py` — psutil snapshot for current + invalid PID
- `test_logging.py` — logger setup
- `test_reports.py` — JSON and CSV generation

**Coverage: 87%** (`pytest --cov=app`). The uncovered lines are the
watchdog event loop in `monitor.py` and the threaded `main.py` entry
point — both need a live process, which is why they're excluded.

### 3.2 End-to-end manual test

1. Start the monitor: `python -m app.detectors.monitor`
2. Run `python simulate_attack.py` in a second terminal
3. Watch: Warning → Critical → incident → quarantine

Verified output:

```
WARNING | Threat level Warning (score 40) - signals: ['rapid_encryption']
WARNING | Threat level Critical (score 70) - signals: ['rapid_encryption', 'mass_rename']
AUDIT | incident_created score=70 level=Critical files=61 pid=1
INFO | Quarantined 11 files to ./data/quarantine
```


### 3.3 Docker verification

`docker compose up` starts the full stack in one container (monitor
thread + uvicorn). Verified on Fedora with SELinux enforcing — host
volumes relabelled with `chcon container_file_t`.

---

## 4. False positive considered

**Scenario:** a legitimate backup or compression tool runs `tar` /
`rsync` / `gzip` over the watch folder. It creates many files rapidly
and produces **high-entropy** output (compressed data looks random).
That is behaviourally identical to ransomware.

**Current behaviour:** RDRS would raise a Critical alert.

**Mitigation idea:** maintain a process whitelist in `config.yaml` and
down-weight signals originating from known-safe processes. The
architecture already supports this — the `unknown_process` signal is
the placeholder for it. Extending the whitelist is a one-file change.

---

## 5. What I would improve next

1. **Real PID attribution.** Currently the incident records the most
   recent process snapshot, not the specific PID that wrote a file. Fix:
   correlate `/proc/<pid>/fd` against write timestamps.
2. **Process whitelist** to eliminate backup-tool false positives.
3. **HTML / PDF reports** using Jinja2 + reportlab (templates not yet
   written).
4. **WebSocket updates** — replace the 3-second polling loop with
   server-push. Would cut idle traffic to near zero.
5. **Full test coverage** — mock `watchdog` and push coverage from
   87% to 95%+.

---

## 6. Files at a glance

```
app/
  core/        config, entropy, logging, process info
  detectors/   file monitor + detection engine
  database/    SQLAlchemy models + CRUD
  api/         FastAPI endpoints
  dashboard/   single-file HTML dashboard
  reports/     JSON / CSV generator
tests/         29 tests
data/          SQLite DB + sandbox folder
logs/          rotating log files
```


---

**Defensive use only.** All testing happens inside `data/sandbox/`.
Never run this on untrusted files or in a production environment without
the quarantine and simulation guarantees intact.

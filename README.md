# RDRS — Ransomware Detection and Response System

A defensive cybersecurity tool that monitors file-system activity,
detects ransomware-like behaviour using a rule-based engine, and raises
alerts with evidence capture.

**Educational project. Defensive use only. Never run real malware.**

## Features

- Real-time file monitoring (create / modify / rename / delete)
- Shannon entropy analysis of modified files
- Sliding-window detection engine (60 s)
- Weighted threat score (Normal / Warning / Critical)
- SQLite storage of events, process snapshots, alerts, incidents
- Incident report generation (JSON + CSV)
- REST API (FastAPI) with automatic docs
- Live dark-theme dashboard
- Docker deployment

## Requirements

- Python 3.12 or newer
- pip, venv
- Optional: Docker, Docker Compose

## Quick Start

### 1. Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

### 2. Run (two terminals)

**Terminal 1 — file monitor:**

    python -m app.detectors.monitor

**Terminal 2 — API + dashboard:**

    uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000

### 3. Open the dashboard

    http://127.0.0.1:8000/static/index.html

### 4. Simulate an attack (Terminal 3)

    python simulate_attack.py

Watch the dashboard turn Critical within a few seconds.

## Generate reports

    python -c "from app.reports.generator import generate_json_report, generate_csv_report; print(generate_json_report()); print(generate_csv_report())"

Creates `report.json` and `report.csv` in the project root.

## Run tests

    pytest -v
    pytest --cov=app --cov-report=term-missing

## Docker

    docker compose up

Then open: http://localhost:8000/static/index.html

## Project Layout

    app/
      core/        config, entropy, logging, process info
      detectors/   file monitor + detection engine
      database/    SQLAlchemy models and CRUD
      api/         FastAPI endpoints
      dashboard/   HTML dashboard
      reports/     JSON / CSV report generator
    tests/         unit + integration tests
    data/          SQLite database + sandbox folder
    logs/          rotating log files

## Safety

This tool is defensive. It does not execute malware, does not modify
user files, and runs in simulation mode by default. All testing is done
inside `data/sandbox/`.

## Author

[Your name] — [Class / Course] — [Date]

"""RDRS REST API."""
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from pathlib import Path as _Path
from fastapi.staticfiles import StaticFiles

from app.database.crud import (
    get_recent_alerts,
    get_recent_events,
    get_incidents,
)
from app.database.models import Session, FileEvent, Alert, Incident, ProcessSnapshot


app = FastAPI(title="RDRS API", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/dashboard/static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status")
def status():
    alerts = get_recent_alerts(limit=1)
    if alerts:
        return {
            "level": alerts[0]["level"],
            "score": alerts[0]["score"],
            "last_alert": alerts[0],
        }
    return {"level": "Normal", "score": 0}


@app.get("/alerts")
def alerts():
    return get_recent_alerts(limit=50)


@app.get("/events")
def events():
    return get_recent_events(limit=200)


@app.get("/reports")
def reports():
    return get_incidents(limit=20)


@app.get("/stats")
def stats():
    """Aggregate counts + latest process + CPU history + quarantine count."""
    try:
        s = Session()
        total_events = s.query(FileEvent).count()
        total_alerts = s.query(Alert).count()
        total_incidents = s.query(Incident).count()

        recent_procs = (
            s.query(ProcessSnapshot)
            .order_by(ProcessSnapshot.timestamp.desc())
            .limit(60)
            .all()
        )
        s.close()

        cpu_history = [
            {"t": p.timestamp.isoformat(), "cpu": float(p.cpu_percent or 0)}
            for p in reversed(recent_procs)
        ]
        latest = recent_procs[0] if recent_procs else None

        q_dir = Path("./data/quarantine")
        q_count = len(list(q_dir.glob("*"))) if q_dir.exists() else 0

        return {
            "total_events": total_events,
            "total_alerts": total_alerts,
            "total_incidents": total_incidents,
            "quarantined_files": q_count,
            "latest_process": (
                {
                    "name": latest.name,
                    "cpu_percent": float(latest.cpu_percent or 0),
                    "memory_percent": float(latest.memory_percent or 0),
                    "pid": latest.pid,
                }
                if latest
                else None
            ),
            "cpu_history": cpu_history,
        }
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/dashboard")
def dashboard():
    """Single-call endpoint returning everything the dashboard needs."""
    return {
        "status": status(),
        "alerts": alerts(),
        "events": events(),
        "reports": reports(),
        "stats": stats(),
    }


@app.post("/scan")
def scan():
    return {"message": "Scan triggered"}


@app.post("/settings")
def settings():
    return {"message": "Settings update"}

# ── File upload: drop a file → watchdog detects it live ──
SANDBOX = Path("./data/sandbox")
SANDBOX.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024   # 10 MB


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Accept a file and save it into the sandbox for live detection."""
    safe_name = Path(file.filename).name  # strip any path components
    if not safe_name:
        return {"ok": False, "error": "Invalid filename"}

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        return {"ok": False, "error": f"File too large (max {MAX_UPLOAD_BYTES // 1024 // 1024} MB)"}

    dest = SANDBOX / safe_name
    # Avoid overwriting — add a numeric suffix if needed
    if dest.exists():
        stem, suffix = dest.stem, dest.suffix
        i = 1
        while dest.exists():
            dest = SANDBOX / f"{stem}_{i}{suffix}"
            i += 1

    dest.write_bytes(content)
    return {"ok": True, "file": dest.name, "size": len(content)}


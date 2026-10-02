"""RDRS entry point: starts the file monitor and the REST API together."""
import threading
import uvicorn

from app.core.logging import setup_logging
from app.database.models import init_db
from app.detectors.monitor import start_monitor


def run_monitor():
    """Run the file-system monitor in its own thread."""
    start_monitor()


def main():
    setup_logging()
    init_db()

    # Background thread: file monitor
    t = threading.Thread(target=run_monitor, daemon=True)
    t.start()

    # Foreground: FastAPI (uvicorn)
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()

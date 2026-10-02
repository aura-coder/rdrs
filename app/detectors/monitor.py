"""Real-time file monitor using watchdog."""
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.core.config import load_config
from app.core.entropy import file_entropy
from app.core.process import get_process_info
from app.core.logging import setup_logging
from app.database.models import init_db
from app.database.crud import add_file_event, add_process_snapshot
from app.detectors.engine import DetectionEngine
from loguru import logger


class RansomwareEventHandler(FileSystemEventHandler):
    """Handle file-system events and feed the detection engine."""

    def __init__(self, engine):
        self.engine = engine
        self._seen = {}

    def on_created(self, event):
        if not event.is_directory:
            self.handle_event('created', event.src_path)

    def on_closed(self, event):
        if not event.is_directory:
            self.handle_event('modified', event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            # Read entropy from the DESTINATION (the renamed file still has the content)
            self.handle_event('moved', event.src_path, event.dest_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.handle_event('deleted', event.src_path)

    def _read_entropy(self, target):
        """Read entropy if file exists and has content. Returns None otherwise."""
        try:
            p = Path(target)
            if not p.exists() or not p.is_file():
                return None
            if p.stat().st_size == 0:
                return None
            return file_entropy(str(p))
        except Exception:
            return None

    def handle_event(self, event_type, src_path, dest_path=None):
        path = dest_path if dest_path else src_path

        # Dedup rapid duplicate events (same type + path within 200ms)
        now = time.time()
        key = f"{event_type}:{path}"
        if now - self._seen.get(key, 0) < 0.2:
            return
        self._seen[key] = now

        ext = Path(path).suffix
        entropy = None

        if event_type == 'moved':
            # Read from destination — content survived the rename
            entropy = self._read_entropy(dest_path)
        elif event_type in ('created', 'modified'):
            # Small pause so the OS flushes the write
            time.sleep(0.03)
            entropy = self._read_entropy(src_path)

        add_file_event(event_type, path, ext, entropy)
        add_process_snapshot(get_process_info())
        self.engine.add_event(event_type, path, ext, entropy)

        suffix = f" (entropy={entropy:.2f})" if entropy is not None else ""
        logger.debug(f"{event_type.upper()} {path}{suffix}")


def start_monitor():
    setup_logging()
    init_db()
    config = load_config()
    folders = config['watch_folders']
    engine = DetectionEngine()
    handler = RansomwareEventHandler(engine)

    observer = Observer()
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        observer.schedule(handler, folder, recursive=True)

    observer.start()
    logger.info(f"Monitoring folders: {folders}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_monitor()

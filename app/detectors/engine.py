"""Detection engine: sliding-window analysis + weighted threat scoring."""
import shutil
from collections import deque
from datetime import datetime, timezone, timedelta
from pathlib import Path

from loguru import logger

from app.core.config import load_config
from app.database.crud import add_alert, add_incident
from app.database.models import Session, ProcessSnapshot


class DetectionEngine:
    """Sliding-window detection engine with weighted threat scoring."""

    def __init__(self):
        self.config = load_config()
        self.window_seconds = self.config.get('window_seconds', 60)
        self.events = deque()
        self.thresholds = self.config['thresholds']
        self.weights = self.config['weights']
        self.quarantine_path = self.config.get('quarantine_path', './data/quarantine')
        self.simulation_mode = self.config.get('simulation_mode', True)
        self.last_level = 'Normal'
        self.incident_created = False

    def add_event(self, event_type, path, extension, entropy=None):
        """Add a file event and re-evaluate the sliding window."""
        now = datetime.now(timezone.utc)
        self.events.append((now, event_type, path, extension, entropy))
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self.events and self.events[0][0] < cutoff:
            self.events.popleft()
        self.evaluate()

    SAFE_PROCESSES = {'python', 'python3', 'python3.12', 'pytest', 'uvicorn', 'bash', 'sh', 'zsh', 'systemd', 'watchdog'}
    CPU_SPIKE_THRESHOLD = 60.0

    def _latest_cpu(self):
        try:
            s = Session()
            snap = s.query(ProcessSnapshot).order_by(ProcessSnapshot.timestamp.desc()).first()
            s.close()
            return float(snap.cpu_percent) if snap and snap.cpu_percent else 0.0
        except Exception:
            return 0.0

    def _suspect_name(self):
        try:
            s = Session()
            snap = s.query(ProcessSnapshot).order_by(ProcessSnapshot.timestamp.desc()).first()
            s.close()
            return (snap.name or '').lower() if snap else ''
        except Exception:
            return ''

    def evaluate(self):
        """Compute signals, score, level, and trigger incident if Critical."""
        if not self.events:
            return

        files_modified = sum(1 for e in self.events if e[1] in ('created', 'modified'))
        renames = sum(1 for e in self.events if e[1] == 'moved')

        # Extension changes — files renamed to suspicious extensions

        SUSPICIOUS_EXT = ('.locked', '.encrypted', '.crypto', '.enc', '.crypt')

        extension_changes = sum(

            1 for ev in self.events

            if ev[1] == 'moved' and ev[3] and ev[3].lower() in SUSPICIOUS_EXT

        )
        entropies = [e[4] for e in self.events if e[4] is not None]
        avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0

        score = 0
        signals = []
        if files_modified > self.thresholds['files_per_minute']:
            score += self.weights['rapid_encryption']
            signals.append('rapid_encryption')
        if renames > self.thresholds['renames_per_minute']:
            score += self.weights['mass_rename']
            signals.append('mass_rename')
        if avg_entropy > self.thresholds['entropy_avg']:
            score += self.weights['high_entropy']
            signals.append('high_entropy')
        if extension_changes > self.thresholds.get('extension_changes_per_minute', 5):
            score += self.weights.get('extension_changes', 20)
            signals.append('extension_changes')

        if self._latest_cpu() > self.CPU_SPIKE_THRESHOLD:
            score += self.weights.get('cpu_spike', 15)
            signals.append('cpu_spike')
        suspect = self._suspect_name()
        if suspect and suspect not in self.SAFE_PROCESSES:
            score += self.weights.get('unknown_process', 10)
            signals.append('unknown_process')
        score = min(score, 100)

        level = 'Normal'
        if score >= 70:
            level = 'Critical'
        elif score >= 40:
            level = 'Warning'

        if level != self.last_level:
            msg = f"Threat level {level} (score {score}) - signals: {signals}"
            logger.warning(msg)
            add_alert(level, score, msg)
            self.last_level = level

            if level == 'Critical' and not self.incident_created:
                affected_files = list(dict.fromkeys(
                    e[2] for e in self.events
                    if e[1] in ('created', 'modified', 'moved')
                ))
                suspect_process = self._get_suspect_process()
                add_incident(score, level, affected_files, suspect_process)
                logger.info(
                    f"AUDIT incident_created score={score} level={level} "
                    f"files={len(affected_files)} pid={suspect_process.get('pid')}"
                )
                logger.critical(
                    f"Incident created with {len(affected_files)} affected files"
                )

                quarantined = self._quarantine_files(affected_files)
                logger.info(
                    f"Quarantined {quarantined} files to {self.quarantine_path}"
                )

                if self.simulation_mode:
                    logger.info(
                        "Simulation mode ON: process termination would be skipped"
                    )

                self.incident_created = True
        elif level != 'Critical':
            self.incident_created = False

    def _get_suspect_process(self):
        """Fetch the most recent process snapshot to attribute as suspect."""
        try:
            session = Session()
            snapshot = (
                session.query(ProcessSnapshot)
                .order_by(ProcessSnapshot.timestamp.desc())
                .first()
            )
            session.close()
            if snapshot:
                return {
                    'pid': snapshot.pid,
                    'name': snapshot.name,
                    'executable': snapshot.executable,
                    'cpu_percent': snapshot.cpu_percent,
                    'memory_percent': snapshot.memory_percent,
                }
        except Exception as exc:
            logger.error(f"Error fetching suspect process: {exc}")
        return {'note': 'No process snapshot available'}

    def _quarantine_files(self, affected_files):
        """Copy affected files into quarantine folder. Never touches originals."""
        quarantine_dir = Path(self.quarantine_path)
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for src in affected_files:
            src_path = Path(src)
            if not src_path.exists() or not src_path.is_file():
                continue
            try:
                dest = quarantine_dir / src_path.name
                if dest.exists():
                    stem = dest.stem
                    suffix = dest.suffix
                    counter = 1
                    while dest.exists():
                        dest = quarantine_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                shutil.copy2(src_path, dest)
                copied += 1
            except Exception as exc:
                logger.error(f"Failed to quarantine {src}: {exc}")
        return copied

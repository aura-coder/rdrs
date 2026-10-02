import json
from datetime import datetime, timezone
from app.database.models import Session, FileEvent, ProcessSnapshot, Alert, Incident

def add_file_event(event_type, path, extension, entropy=None):
    session = Session()
    event = FileEvent(
        event_type=event_type,
        path=str(path),
        extension=extension,
        entropy=entropy,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(event)
    session.commit()
    session.close()

def add_process_snapshot(proc_info):
    if not proc_info:
        return
    session = Session()
    snapshot = ProcessSnapshot(
        pid=proc_info['pid'],
        name=proc_info['name'],
        cpu_percent=proc_info['cpu_percent'],
        memory_percent=proc_info['memory_percent'],
        disk_writes=proc_info['disk_writes'],
        executable=proc_info['executable'],
        parent_pid=proc_info['parent_pid'],
        timestamp=datetime.now(timezone.utc)
    )
    session.add(snapshot)
    session.commit()
    session.close()

def add_alert(level, score, message):
    session = Session()
    alert = Alert(
        level=level,
        score=score,
        message=message,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(alert)
    session.commit()
    session.close()

def add_incident(score, level, affected_files, suspect_process):
    session = Session()
    incident = Incident(
        score=score,
        level=level,
        affected_files=json.dumps(affected_files),
        suspect_process=json.dumps(suspect_process),
        timestamp=datetime.now(timezone.utc)
    )
    session.add(incident)
    session.commit()
    session.close()

def get_recent_alerts(limit=10):
    session = Session()
    alerts = session.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
    session.close()
    return [
        {
            'id': a.id,
            'level': a.level,
            'score': a.score,
            'message': a.message,
            'timestamp': a.timestamp.isoformat()
        } for a in alerts
    ]

def get_recent_events(limit=10):
    session = Session()
    events = session.query(FileEvent).order_by(FileEvent.timestamp.desc()).limit(limit).all()
    session.close()
    return [
        {
            'id': e.id,
            'event_type': e.event_type,
            'path': e.path,
            'extension': e.extension,
            'entropy': e.entropy,
            'timestamp': e.timestamp.isoformat()
        } for e in events
    ]

def get_incidents(limit=10):
    session = Session()
    incidents = session.query(Incident).order_by(Incident.timestamp.desc()).limit(limit).all()
    session.close()
    return [
        {
            'id': i.id,
            'score': i.score,
            'level': i.level,
            'affected_files': json.loads(i.affected_files),
            'suspect_process': json.loads(i.suspect_process),
            'timestamp': i.timestamp.isoformat()
        } for i in incidents
    ]

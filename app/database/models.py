from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from app.core.config import load_config

config = load_config()
db_path = config.get('database_path', './data/rdrs.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class FileEvent(Base):
    __tablename__ = 'file_events'
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    path = Column(String)
    extension = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    entropy = Column(Float, nullable=True)

class ProcessSnapshot(Base):
    __tablename__ = 'process_snapshots'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    name = Column(String)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_writes = Column(Integer)
    executable = Column(String)
    parent_pid = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    level = Column(String)
    score = Column(Integer)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    level = Column(String)
    affected_files = Column(Text)
    suspect_process = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)

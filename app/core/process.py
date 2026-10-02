import psutil

def get_process_info(pid=None):
    if pid is None:
        pid = psutil.Process().pid
    try:
        p = psutil.Process(pid)
        return {
            'pid': pid,
            'name': p.name(),
            'cpu_percent': p.cpu_percent(interval=0.1),
            'memory_percent': p.memory_percent(),
            'disk_writes': p.io_counters().write_bytes if p.io_counters() else 0,
            'executable': p.exe(),
            'parent_pid': p.ppid()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

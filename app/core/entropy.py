import math

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    entropy = 0.0
    length = len(data)
    for c in counts:
        if c:
            p = c / length
            entropy -= p * math.log2(p)
    return entropy

def file_entropy(path: str, sample_size: int = 65536) -> float:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(sample_size)
        return shannon_entropy(chunk)
    except Exception:
        return 0.0

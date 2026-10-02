"""Safe ransomware-like behaviour simulator. Sandbox only."""
import os
import pathlib
import time

sandbox = pathlib.Path('data/sandbox')
sandbox.mkdir(parents=True, exist_ok=True)

# Clean previous runs
for f in sandbox.glob('*'):
    f.unlink()

print("Creating 50 normal files...")
for i in range(50):
    (sandbox / f'file_{i}.txt').write_text('normal document content')
    time.sleep(0.02)

print("Simulating attack: overwriting with random bytes and renaming to .locked")
for f in list(sandbox.glob('*.txt')):
    f.write_bytes(os.urandom(20000))
    time.sleep(0.05)                # let the write flush before rename
    f.rename(f.with_suffix('.locked'))
    time.sleep(0.02)

print("Simulation complete.")

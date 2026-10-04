"""Manual Developer Utility: Seed initial projects into Firebase Realtime Database.
This script acts as the Execution Layer script in the 3-Layer Architecture.
It delegates to the original backend script to maintain compatibility.
"""
import sys
import subprocess
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    backend_script = root_dir / "backend" / "scripts" / "seed_database.py"

    if not backend_script.exists():
        print(f"Error: Could not find script at {backend_script}")
        sys.exit(1)

    print(f"Delegating execution to {backend_script} ...")
    # Execute the backend script directly via subprocess
    result = subprocess.run([sys.executable, str(backend_script)] + sys.argv[1:])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()

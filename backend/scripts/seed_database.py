"""Manual Developer Utility: Seed initial projects into Firebase Realtime Database.

IMPORTANT:
This script NEVER runs automatically during startup or deployment.
It requires explicit manual execution by a developer with --confirm.
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.config import FIREBASE_DATABASE_URL, PROJECTS_FILE
from app.services.firebase_service import save_project_to_firebase


def main():
    parser = argparse.ArgumentParser(
        description="Explicitly seed reference projects into Firebase Realtime Database."
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Explicit confirmation required to write to Firebase Realtime Database.",
    )
    args = parser.parse_args()

    if not args.confirm:
        print("SAFETY ABORT: This script will NOT run without the explicit --confirm flag.")
        print("Usage: python seed_database.py --confirm")
        sys.exit(1)

    if not FIREBASE_DATABASE_URL:
        print("ERROR: FIREBASE_DATABASE_URL is not set in backend/.env.")
        print("Please configure your Firebase Realtime Database URL before seeding.")
        sys.exit(1)

    if not PROJECTS_FILE.is_file():
        print(f"ERROR: Projects source file not found at {PROJECTS_FILE}")
        sys.exit(1)

    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    projects = data.get("projects", [])
    print(f"Loaded {len(projects)} reference projects from {PROJECTS_FILE.name}")
    print(f"Target Database: {FIREBASE_DATABASE_URL}")

    success_count = 0
    for p in projects:
        p_id = p.get("project_id")
        if not p_id:
            continue
        print(f"Seeding project {p_id}: {p.get('name')}...")
        if save_project_to_firebase(p_id, p):
            success_count += 1
        else:
            print(f"Failed to seed {p_id}")

    print(f"\nDone! Successfully seeded {success_count}/{len(projects)} projects into Firebase.")


if __name__ == "__main__":
    main()

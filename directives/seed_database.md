# Directive: Seed Reference Projects Database

## Goal
To seed the Firebase Realtime Database with initial reference projects when setting up the environment.

## Inputs
- Explicit confirmation to proceed.

## Tools / Scripts
- `execution/seed_database.py`

## Outputs
- Logs confirming the number of successfully seeded projects.

## Edge Cases
- If the user forgets to supply `--confirm`, the script will fail gracefully with a safety abort message.
- If the environment variables (like `FIREBASE_DATABASE_URL`) are not set, it will report an error.

## Execution Flow
1. Verify if the user wants to seed the database (prompt for confirmation if unclear).
2. Run `python execution/seed_database.py --confirm`.
3. Report success or failure based on the terminal output.

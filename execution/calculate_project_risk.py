"""Deterministic execution script to calculate base risk metrics for a project.
This script uses existing deterministic functions from the backend to ensure
consistency across the platform without rewriting business logic.
"""
import argparse
import sys
import json
from pathlib import Path

# Add backend directory to sys.path to import existing services
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.project_service import get_project_by_id
from app.services.risk_engine import calculate_risk

def main():
    parser = argparse.ArgumentParser(description="Calculate deterministic risk for a given project ID.")
    parser.add_argument("--project-id", required=True, help="The ID of the project to analyze")
    args = parser.parse_args()

    try:
        project = get_project_by_id(args.project_id)
    except Exception as e:
        print(f"Error accessing database: {e}")
        sys.exit(1)

    if not project:
        print(f"Error: Project {args.project_id} not found in database.")
        sys.exit(1)

    risk_breakdown = calculate_risk(project)
    
    # Output the result as JSON for the orchestration layer to consume
    result = {
        "project_id": args.project_id,
        "overall_score": risk_breakdown.overall_score,
        "overall_level": risk_breakdown.overall_level,
        "progress_risk": risk_breakdown.progress_risk,
        "delay_risk": risk_breakdown.delay_risk,
        "budget_risk": risk_breakdown.budget_risk,
        "major_factors": risk_breakdown.major_factors
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

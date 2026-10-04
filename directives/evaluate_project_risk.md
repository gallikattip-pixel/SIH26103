# Directive: Evaluate Project Risk

## Goal
To retrieve deterministic risk metrics for a specific project before passing data to an AI model for deeper synthesis.

## Inputs
- `project_id`: The ID of the project to evaluate.

## Tools / Scripts
- `execution/calculate_project_risk.py`

## Outputs
- A JSON object containing the overall risk score, level, risk components (progress, delay, budget), and major risk factors.

## Edge Cases
- If the `project_id` is invalid or missing from the database, the script will error out. Inform the user that the project was not found.

## Execution Flow
1. Run `python execution/calculate_project_risk.py --project-id <project_id>`.
2. Parse the JSON output from the script.
3. Use these deterministic metrics as context when writing reports or passing context to AI for natural language summarization. DO NOT use LLMs to calculate these baseline metrics.

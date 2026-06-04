# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

Automate Apart Research's post-Sprint pipeline. Currently each Sprint costs ops 6-8 hours of manual work: exporting CSVs from Typeform, spreadsheet wrangling, emailing judges, tallying scores, posting Discord results. This pipeline eliminates all of that.

## What This Pipeline Does

1. **Ingest** — reads participant/submission data from a CSV file
2. **Assign** — auto-assigns submissions to judges using round-robin per track
3. **Email** — generates personalised judge briefing emails as a JSON file (ready to send)
4. **Score** — calculates team scores, ranks them into a leaderboard
5. **Discord** — posts a formatted results summary to a Discord channel via webhook

Each step is a standalone module. `main.py` orchestrates all five in sequence.

## Architecture

```
test-project/
├── main.py                  # Orchestrator: runs all 5 pipeline steps in order
├── pipeline/
│   ├── ingest.py            # CSV → validated pandas DataFrame
│   ├── assign.py            # Round-robin judge assignment by track → assignments.json
│   ├── emails.py            # Per-judge project list → judge_emails.json
│   ├── scoring.py           # Avg scores → ranked leaderboard → leaderboard.csv
│   └── discord_post.py      # Format + POST leaderboard to Discord webhook
├── data/
│   └── sample_submissions.csv  # Realistic test data for local runs
├── output/                  # Generated files land here (gitignored)
│   ├── assignments.json
│   ├── judge_emails.json
│   └── leaderboard.csv
└── README.md
```

Each `pipeline/` module exposes one primary function called by `main.py`. Modules do not import each other — data flows through `main.py` as DataFrames or dicts.

## Running the Pipeline

```bash
# Run full pipeline end-to-end
python main.py

# Run with a custom CSV
python main.py --input data/my_sprint.csv
```

## Development Approach

- **One module at a time.** Write → test locally → approve → next module.
- **No placeholders.** Every function must be working and testable.
- **Test each module standalone** by running it directly (`python pipeline/ingest.py`).
- Use `rich` for all console output (progress, tables, errors).
- Use `pandas` for all data manipulation.
- Use `jinja2` for email template rendering.

## CSV Input Schema

Expected columns in the input CSV:

| Column | Description |
|--------|-------------|
| `team_name` | Team identifier |
| `track` | Hackathon track (e.g. "AI Safety", "Interpretability") |
| `project_url` | Link to submission |
| `score_innovation` | Float 0–10 |
| `score_feasibility` | Float 0–10 |
| `score_impact` | Float 0–10 |
| `judge_email` | Assigned judge's email |

## Key Config

Discord webhook URL is stored in `README.md` temporarily (under `## Temp`). Before any production use, move to a `.env` file and add `.env` to `.gitignore`.

## Tools Used

- **Python 3.x**
- **pandas** — data ingestion, manipulation, scoring
- **rich** — terminal output formatting
- **jinja2** — email template rendering
- **requests** — Discord webhook POST

## Judgment Calls

- Round-robin assignment is per-track so each judge sees submissions from the same domain.
- Scores are averaged across 3 dimensions (innovation, feasibility, impact) with equal weight.
- Email output is JSON, not sent directly — keeps the tool decoupled from any email provider.
- Discord post uses embeds for readability; top 3 teams are highlighted.

## What More Time Would Add

- Typeform API integration (skip CSV export entirely)
- Weighted scoring config per Sprint
- Email sending via SendGrid/Resend
- Web UI for ops team (no CLI needed)
- GitHub Actions workflow to trigger pipeline on CSV upload

## Open Questions

- Should judges be able to score the same team independently and scores averaged, or is one judge per team final?
- What's the tiebreaker rule for equal scores?
- Is track assignment always in the CSV, or does the pipeline need to infer it?

# Apart Research — Post-Sprint Automation Pipeline

> **What this does in plain English:** After every Sprint, someone used to spend 6–8 hours manually copying data between spreadsheets, emailing judges one by one, tallying scores by hand, and writing a Discord post. This pipeline does all of that in under 10 seconds with a single command.

---

## How to Run It

```bash
# Install dependencies (one-time)
pip install pandas rich jinja2 requests

# Run the full pipeline with sample data
python main.py

# Run with your own CSV
python main.py --input path/to/your_sprint.csv
```

That's it. The pipeline prints live progress to your terminal and produces three output files:

| File | What's in it |
|------|-------------|
| `output/assignments.json` | Which judge is assigned to which submission |
| `output/judge_emails.json` | Ready-to-send briefing email for each judge |
| `output/leaderboard.csv` | All teams ranked by score |

It also posts the final leaderboard directly to your Discord channel.

---

## What the Pipeline Does, Step by Step

Think of it as a five-stage conveyor belt. Each stage hands its output to the next.

### Stage 1 — Ingest (`pipeline/ingest.py`)
Reads the CSV file exported from Typeform (or any source). Validates that all required columns are present. Cleans up whitespace, ensures scores are numbers between 0 and 10, and drops any duplicate team entries. If something looks wrong, it tells you exactly what's missing rather than crashing silently.

### Stage 2 — Assign (`pipeline/assign.py`)
Goes through each hackathon track (e.g. "AI Safety", "Interpretability") and distributes submissions to judges in a round-robin pattern. This means if a track has three submissions and two judges, Judge A gets submissions 1 and 3, Judge B gets submission 2. No one gets overloaded by accident.

### Stage 3 — Emails (`pipeline/emails.py`)
Generates a personalised email for each judge listing exactly which projects they need to review, with direct links. Output is saved as JSON so you can feed it into any email provider (SendGrid, Resend, Gmail API) without changing this code.

### Stage 4 — Scoring (`pipeline/scoring.py`)
Calculates each team's total score by averaging three dimensions: Innovation, Feasibility, and Impact (each scored 0–10). Teams are ranked highest to lowest. Ties are broken by Impact first, then Innovation, then Feasibility.

### Stage 5 — Discord (`pipeline/discord_post.py`)
Formats the leaderboard as a Discord embed with a podium section (1st/2nd/3rd) and a full results table, then POSTs it to the configured webhook URL. No manual copy-pasting needed.

---

## Input CSV Format

Your CSV must have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `team_name` | Team name | `NeuralNomads` |
| `track` | Hackathon track | `AI Safety` |
| `project_url` | Link to submission | `https://github.com/...` |
| `score_innovation` | Score 0–10 | `8.5` |
| `score_feasibility` | Score 0–10 | `7.0` |
| `score_impact` | Score 0–10 | `9.0` |
| `judge_email` | Judge's email | `alice@apart.ai` |

A sample file is included at `data/sample_submissions.csv` with 12 realistic entries across 3 tracks.

---

## Tools Used

| Tool | Why |
|------|-----|
| **Python** | Core language |
| **pandas** | Data loading, cleaning, scoring calculations |
| **rich** | Formatted terminal output — tables, panels, progress |
| **jinja2** | Email templating (separates content from structure) |
| **requests** | HTTP POST to Discord webhook |

---

## Approach

The goal was to replace every manual step in the post-Sprint ops workflow with a deterministic, testable Python function. Each step is isolated in its own module so it can be developed, tested, and debugged independently. The `main.py` orchestrator is intentionally thin — it just calls each module in order and reports results.

Data flows as pandas DataFrames between stages, never as raw strings or dicts, so each module can rely on typed, validated data from the previous step.

---

## Judgment Calls

- **Round-robin is per-track**, not global. Judges are domain experts — it makes no sense to send an Interpretability specialist someone's Alignment project.
- **Equal score weights** (Innovation = Feasibility = Impact). Without a stated weighting from Apart Research, equal weights are the safest default. Easy to change in `scoring.py`.
- **Email output is JSON, not sent directly.** Keeping the sending step separate means this tool works regardless of which email provider Apart uses — no vendor lock-in.
- **Tiebreaker order: Impact > Innovation > Feasibility.** Impact felt like the most mission-aligned dimension for Apart Research's goals.

---

## What I'd Do With More Time

1. **Typeform API integration** — skip the CSV export step entirely; pull data directly after the Sprint closes
2. **Weighted scoring config** — a simple YAML file per Sprint to adjust score weights without touching code
3. **Email sending** — wire `judge_emails.json` directly to SendGrid or Resend
4. **Multi-judge per submission** — average scores from multiple independent judges per team (currently assumes one judge per track)
5. **GitHub Actions workflow** — trigger the pipeline automatically when a CSV is pushed to the repo

---

## Open Questions

- Should multiple judges score the same submission independently, with scores averaged? The current model assigns one judge per submission.
- Is the tiebreaker order (Impact > Innovation > Feasibility) correct for Apart's priorities?
- Should judges from one track ever review submissions from another track if the workload is uneven?
- Is the `judge_email` column in the CSV the *preferred* judge, or just a starting point that the pipeline can override?

---

## Where the Time Cutoff Hit

Built in order: project structure → ingest → assign → emails → scoring → Discord → main orchestrator → README. The Discord module and `main.py` were the last pieces before the cutoff. With more time the priority would be multi-judge scoring and the Typeform API integration, as those are the highest-leverage improvements for real Sprint ops.

---

## Temp Config

DISCORD_WEBHOOK=https://discord.com/api/webhooks/1512087099984318474/xJpGHz9VwJz7wBl_po4ON3jLKiFFToscee43IIXJg0nU7ui5epsOHqSIukmOz4O8tGDr

> Remove this before making the repo public or sharing widely.

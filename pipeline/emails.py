import json
import pandas as pd
from jinja2 import Template
from rich.console import Console
from rich.panel import Panel

console = Console()

EMAIL_TEMPLATE = Template("""\
Subject: [Apart Sprint] Your Judge Briefing — {{ track }} Track

Hi {{ judge_name }},

Thank you for judging the {{ track }} track at this Apart Research Sprint!

You have been assigned {{ submissions | length }} submission(s) to review:

{% for s in submissions %}
{{ loop.index }}. **{{ s.team_name }}**
   Project URL: {{ s.project_url }}
   Track: {{ s.track }}

{% endfor %}
Please score each project on three dimensions (0–10):
  - Innovation: How novel or creative is the approach?
  - Feasibility: How realistic is implementation?
  - Impact: How significant could the real-world effect be?

Submit your scores via the scoring form by the deadline.

Thanks again for your time and expertise!

— The Apart Research Team
""")


def generate_emails(df: pd.DataFrame, output_path: str = "output/judge_emails.json") -> list:
    """
    Generate one personalised briefing email per judge.
    Returns list of email dicts. Writes judge_emails.json to output_path.
    """
    console.print("\n[bold cyan]EMAILS[/bold cyan] Generating judge briefing emails")

    assign_col = "assigned_judge" if "assigned_judge" in df.columns else "judge_email"

    emails = []
    for judge_email, group in df.groupby(assign_col):
        judge_name = judge_email.split("@")[0].capitalize()
        track = group["track"].iloc[0]

        submissions = [
            {
                "team_name": row["team_name"],
                "project_url": row["project_url"],
                "track": row["track"],
            }
            for _, row in group.iterrows()
        ]

        body = EMAIL_TEMPLATE.render(
            judge_name=judge_name,
            track=track,
            submissions=submissions,
        )

        emails.append({
            "to": judge_email,
            "judge_name": judge_name,
            "track": track,
            "submission_count": len(submissions),
            "body": body,
        })

        console.print(Panel(
            body,
            title=f"[bold]{judge_email}[/bold] ({len(submissions)} submission(s))",
            border_style="blue",
            expand=False,
        ))

    with open(output_path, "w") as f:
        json.dump(emails, f, indent=2)

    console.print(f"\n[green]{len(emails)} email(s) written to {output_path}[/green]")
    return emails


if __name__ == "__main__":
    from ingest import load_submissions
    from assign import assign_judges
    df = load_submissions("data/sample_submissions.csv")
    df = assign_judges(df)
    generate_emails(df)

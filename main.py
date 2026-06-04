import argparse
import sys
from rich.console import Console
from rich.rule import Rule

console = Console()

# Add pipeline/ to path so modules import cleanly
sys.path.insert(0, "pipeline")

from pipeline.ingest import load_submissions
from pipeline.assign import assign_judges
from pipeline.emails import generate_emails
from pipeline.scoring import calculate_scores
from pipeline.discord_post import post_to_discord


def run(csv_path: str, webhook_url: str = None):
    console.print(Rule("[bold]Apart Research Sprint Pipeline[/bold]"))
    console.print(f"[dim]Input: {csv_path}[/dim]\n")

    # Step 1: Ingest
    df = load_submissions(csv_path)

    # Step 2: Assign judges
    df_assigned = assign_judges(df)

    # Step 3: Generate judge emails
    generate_emails(df_assigned)

    # Step 4: Score + leaderboard
    leaderboard = calculate_scores(df_assigned)

    # Step 5: Post to Discord
    kwargs = {"webhook_url": webhook_url} if webhook_url else {}
    success = post_to_discord(leaderboard, **kwargs)

    console.print(Rule("[bold green]Pipeline Complete[/bold green]"))
    console.print("[green]All steps finished.[/green]")
    console.print("  output/assignments.json   — judge assignments")
    console.print("  output/judge_emails.json  — briefing emails")
    console.print("  output/leaderboard.csv    — ranked results")
    if success:
        console.print("  Discord                   — results posted")

    return leaderboard


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apart Research Sprint Pipeline")
    parser.add_argument(
        "--input",
        default="data/sample_submissions.csv",
        help="Path to submissions CSV (default: data/sample_submissions.csv)",
    )
    parser.add_argument(
        "--webhook",
        default=None,
        help="Discord webhook URL (overrides default in discord_post.py)",
    )
    args = parser.parse_args()
    run(args.input, args.webhook)

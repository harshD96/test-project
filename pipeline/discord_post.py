import requests
import pandas as pd
from rich.console import Console

console = Console()

WEBHOOK_URL = "https://discord.com/api/webhooks/1512087099984318474/xJpGHz9VwJz7wBl_po4ON3jLKiFFToscee43IIXJg0nU7ui5epsOHqSIukmOz4O8tGDr"

PLACE_LABELS = {1: "1st", 2: "2nd", 3: "3rd"}


def post_to_discord(leaderboard: pd.DataFrame, webhook_url: str = WEBHOOK_URL) -> bool:
    """
    Format leaderboard as a Discord embed and POST to webhook.
    Top 3 teams highlighted. Returns True on success.
    """
    console.print("\n[bold cyan]DISCORD[/bold cyan] Posting results to Discord")

    top3 = leaderboard.head(3)
    rest = leaderboard.iloc[3:]

    # Build podium block
    podium_lines = []
    for _, row in top3.iterrows():
        rank = int(row["rank"])
        label = PLACE_LABELS.get(rank, f"#{rank}")
        podium_lines.append(
            f"**{label} — {row['team_name']}** ({row['track']}) — Score: `{row['total_score']:.2f}`\n"
            f"> {row['project_url']}"
        )

    # Build full results block
    full_lines = ["```"]
    full_lines.append(f"{'Rank':<5} {'Team':<20} {'Track':<18} {'Score':>6}")
    full_lines.append("-" * 52)
    for _, row in leaderboard.iterrows():
        full_lines.append(
            f"{int(row['rank']):<5} {row['team_name']:<20} {row['track']:<18} {row['total_score']:>6.2f}"
        )
    full_lines.append("```")

    embed = {
        "title": "Apart Research Sprint — Final Results",
        "description": "The Sprint has concluded. Here are the final rankings!",
        "color": 0x5865F2,
        "fields": [
            {
                "name": "Podium",
                "value": "\n\n".join(podium_lines),
                "inline": False,
            },
            {
                "name": "Full Leaderboard",
                "value": "\n".join(full_lines),
                "inline": False,
            },
        ],
        "footer": {"text": "Scores: avg of Innovation + Feasibility + Impact (0-10 each)"},
    }

    payload = {"embeds": [embed]}

    console.print("[dim]Sending to Discord...[/dim]")
    response = requests.post(webhook_url, json=payload)

    if response.status_code in (200, 204):
        console.print("[green]Discord post successful![/green]")
        return True
    else:
        console.print(f"[bold red]Discord POST failed: {response.status_code} — {response.text}[/bold red]")
        return False


if __name__ == "__main__":
    from ingest import load_submissions
    from scoring import calculate_scores
    df = load_submissions("data/sample_submissions.csv")
    leaderboard = calculate_scores(df)
    post_to_discord(leaderboard)

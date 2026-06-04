import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

SCORE_COLUMNS = ["score_innovation", "score_feasibility", "score_impact"]
MEDALS = {1: "#1", 2: "#2", 3: "#3"}


def calculate_scores(df: pd.DataFrame, output_path: str = "output/leaderboard.csv") -> pd.DataFrame:
    """
    Average the 3 score columns per team, rank descending.
    Tiebreaker: score_impact > score_innovation > score_feasibility.
    Writes leaderboard.csv to output_path. Returns ranked DataFrame.
    """
    console.print("\n[bold cyan]SCORING[/bold cyan] Calculating scores and building leaderboard")

    leaderboard = df.copy()
    leaderboard["total_score"] = leaderboard[SCORE_COLUMNS].mean(axis=1).round(2)

    leaderboard = leaderboard.sort_values(
        by=["total_score", "score_impact", "score_innovation", "score_feasibility"],
        ascending=False,
    ).reset_index(drop=True)

    leaderboard.insert(0, "rank", leaderboard.index + 1)

    out_cols = ["rank", "team_name", "track", "total_score"] + SCORE_COLUMNS + ["project_url"]
    leaderboard[out_cols].to_csv(output_path, index=False)

    _print_leaderboard(leaderboard)
    console.print(f"\n[green]Leaderboard written to {output_path}[/green]")
    return leaderboard


def _print_leaderboard(df: pd.DataFrame):
    table = Table(title="Sprint Leaderboard", show_lines=True)
    table.add_column("Rank", justify="center", style="bold")
    table.add_column("Team", style="bold")
    table.add_column("Track")
    table.add_column("Total", justify="right", style="bold yellow")
    table.add_column("Innovation", justify="right")
    table.add_column("Feasibility", justify="right")
    table.add_column("Impact", justify="right")

    for _, row in df.iterrows():
        rank = int(row["rank"])
        medal = MEDALS.get(rank, str(rank))
        table.add_row(
            medal,
            row["team_name"],
            row["track"],
            f"{row['total_score']:.2f}",
            f"{row['score_innovation']:.1f}",
            f"{row['score_feasibility']:.1f}",
            f"{row['score_impact']:.1f}",
        )

    console.print(table)


if __name__ == "__main__":
    from ingest import load_submissions
    df = load_submissions("data/sample_submissions.csv")
    calculate_scores(df)

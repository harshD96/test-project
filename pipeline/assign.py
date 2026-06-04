import json
import pandas as pd
from itertools import cycle
from rich.console import Console
from rich.table import Table

console = Console()


def assign_judges(df: pd.DataFrame, output_path: str = "output/assignments.json") -> pd.DataFrame:
    """
    Round-robin assign judges to submissions within each track.
    Each track's judge pool is derived from judges already present in that track's rows.
    Returns df with 'assigned_judge' column added.
    Writes assignments.json to output_path.
    """
    console.print("\n[bold cyan]ASSIGN[/bold cyan] Assigning judges per track (round-robin)")

    assigned_rows = []

    for track, group in df.groupby("track"):
        judges = sorted(group["judge_email"].unique().tolist())
        judge_cycle = cycle(judges)

        for _, row in group.iterrows():
            row = row.copy()
            row["assigned_judge"] = next(judge_cycle)
            assigned_rows.append(row)

    result = pd.DataFrame(assigned_rows).reset_index(drop=True)

    assignments = []
    for _, row in result.iterrows():
        assignments.append({
            "team_name": row["team_name"],
            "track": row["track"],
            "project_url": row["project_url"],
            "assigned_judge": row["assigned_judge"],
        })

    with open(output_path, "w") as f:
        json.dump(assignments, f, indent=2)

    _print_summary(result, output_path)
    return result


def _print_summary(df: pd.DataFrame, output_path: str):
    table = Table(title="Judge Assignments", show_lines=True)
    table.add_column("Team", style="bold")
    table.add_column("Track")
    table.add_column("Assigned Judge")

    for _, row in df.iterrows():
        table.add_row(row["team_name"], row["track"], row["assigned_judge"])

    console.print(table)

    by_judge = df.groupby("assigned_judge")["team_name"].count()
    console.print("\n[bold]Workload per judge:[/bold]")
    for judge, count in by_judge.items():
        console.print(f"  {judge}: {count} submission(s)")

    console.print(f"\n[green]Assignments written to {output_path}[/green]")


if __name__ == "__main__":
    from ingest import load_submissions
    df = load_submissions("data/sample_submissions.csv")
    assign_judges(df)

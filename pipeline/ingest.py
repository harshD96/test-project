import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

REQUIRED_COLUMNS = {
    "team_name", "track", "project_url",
    "score_innovation", "score_feasibility", "score_impact",
    "judge_email",
}

SCORE_COLUMNS = ["score_innovation", "score_feasibility", "score_impact"]


def load_submissions(csv_path: str) -> pd.DataFrame:
    console.print(f"\n[bold cyan]INGEST[/bold cyan] Loading: [yellow]{csv_path}[/yellow]")

    df = pd.read_csv(csv_path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        console.print(f"[bold red]Missing columns: {missing}[/bold red]")
        raise ValueError(f"CSV missing required columns: {missing}")

    df.columns = df.columns.str.strip()
    df["team_name"] = df["team_name"].str.strip()
    df["track"] = df["track"].str.strip()
    df["judge_email"] = df["judge_email"].str.strip().str.lower()

    for col in SCORE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        invalid = df[col].isna().sum()
        if invalid:
            console.print(f"[yellow]Warning: {invalid} non-numeric value(s) in '{col}' set to 0[/yellow]")
        df[col] = df[col].fillna(0).clip(0, 10)

    df = df.drop_duplicates(subset=["team_name"])

    _print_summary(df)
    return df


def _print_summary(df: pd.DataFrame):
    table = Table(title="Loaded Submissions", show_lines=True)
    table.add_column("Team", style="bold")
    table.add_column("Track")
    table.add_column("Judge")
    table.add_column("Innovation", justify="right")
    table.add_column("Feasibility", justify="right")
    table.add_column("Impact", justify="right")

    for _, row in df.iterrows():
        table.add_row(
            row["team_name"],
            row["track"],
            row["judge_email"],
            f"{row['score_innovation']:.1f}",
            f"{row['score_feasibility']:.1f}",
            f"{row['score_impact']:.1f}",
        )

    console.print(table)
    console.print(f"[green]{len(df)} submissions loaded across {df['track'].nunique()} tracks[/green]")


if __name__ == "__main__":
    df = load_submissions("data/sample_submissions.csv")
    print(df.dtypes)

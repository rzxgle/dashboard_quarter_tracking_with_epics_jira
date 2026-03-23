from datetime import date
from config import QUARTER_START, QUARTER_END

def calculate_epic_progress(df):

    epic_progress = (
        df.groupby(["team", "epic"])
        .agg(
            total_items=("issue", "count"),
            completed_items=("done", "sum")
        )
        .reset_index()
    )

    epic_progress["progress"] = (
        epic_progress["completed_items"] /
        epic_progress["total_items"]
    ) * 100

    return epic_progress


def calculate_team_progress(epic_progress):

    team_progress = (
        epic_progress
        .groupby("team")
        .agg(
            total_items=("total_items", "sum"),
            completed_items=("completed_items", "sum")
        )
        .reset_index()
    )
    
    team_progress["progress"] = (
    team_progress["completed_items"] /
    team_progress["total_items"]
    )

    team_progress["progress"] = team_progress["progress"].fillna(0) * 100

    return team_progress


def calculate_cluster_progress(team_progress):

    total_items = team_progress["total_items"].sum()
    completed_items = team_progress["completed_items"].sum()

    if total_items == 0:
        return 0

    return (completed_items / total_items) * 100

def calculate_quarter_time_progress():

    today = date.today()

    total_days = (QUARTER_END - QUARTER_START).days
    elapsed_days = (today - QUARTER_START).days

    if elapsed_days < 0:
        return 0

    if elapsed_days > total_days:
        return 100

    return (elapsed_days / total_days) * 100

def calculate_risk_metrics(epic_progress, team_progress, expected_progress):

    epics_at_risk = epic_progress[
        epic_progress["progress"] < expected_progress
    ].shape[0]

    squads_at_risk = team_progress[
        team_progress["progress"] < expected_progress
    ].shape[0]

    total_epics = epic_progress.shape[0]

    return squads_at_risk, epics_at_risk, total_epics
import pandas as pd
from config import *
from domain.workflow_rules import get_priority

def issues_to_dataframe(issues):

    data = []

    for issue in issues:
        epic = None

        if hasattr(issue.fields, "parent") and issue.fields.parent:
            epic = issue.fields.parent.key

        if not epic:
            epic = "No Epic"
            
        flags = getattr(issue.fields, "customfield_10500", None)

        flagged = False

        try:
            if flags:
                flagged = any(
                    getattr(f, "value", "") == "Impedimento"
                    for f in flags
                )
        except:
            flagged = False
            
        team_obj = getattr(issue.fields, TEAM_FIELD, None)
        team = team_obj.name if team_obj else "Unknown Team"

        status_category = issue.fields.status.statusCategory.name
        done = 1 if status_category == "Done" else 0
        
        summary = issue.fields.summary
        status = issue.fields.status.name
        
        priority = get_priority(status, done, flagged)

        data.append({
            "issue": issue.key,
            "summary": summary,
            "epic": epic,
            "team": team,
            "status": status,
            "done": done,
            "flagged": flagged,
            "priority": priority
        })

    df = pd.DataFrame(data)
    
    if df.empty:
        df = pd.DataFrame(columns=[
            "issue",
            "summary",
            "epic",
            "team",
            "status",
            "done",
            "flagged",
            "priority"
        ])

    return df
import streamlit as st
from jira import JIRA
import pandas as pd
from config import *


def get_jira_client():

    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_TOKEN)
    )

@st.cache_data(ttl=300, show_spinner=False)
def fetch_issues(jql):

    jira = get_jira_client()

    epics = jira.search_issues(
        jql,
        maxResults=False,
        fields=["summary", TEAM_FIELD] 
    )

    epic_map = {epic.key: epic.fields.summary for epic in epics}

    epic_data = []

    for epic in epics:
        team_obj = getattr(epic.fields, TEAM_FIELD, None)
        team = team_obj.name if team_obj else "Unknown Team"

        epic_data.append({
            "epic": epic.key,
            "team": team
        })

    epic_df = pd.DataFrame(epic_data)

    epic_keys = list(epic_map.keys())

    if not epic_keys:
        return [], {}, epic_df

    epic_string = ",".join(epic_keys)

    issues = jira.search_issues(
        f'parent in ({epic_string}) AND status not in (Inválido, Cancelado)',
        maxResults=False
    )

    return issues, epic_map, epic_df
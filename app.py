import streamlit as st
import pandas as pd
from datetime import date
from services.jira_client import fetch_issues
from utils.data_processing import issues_to_dataframe
from utils.period_utils import get_quarter_dates, get_current_quarter
from domain.safe_metrics import *
from ui.team_view import render_teams

st.set_page_config(
    page_title="ART Progress Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("🚀 Afya - Quarter Tracking")

label = st.text_input(
    "Label do Épico",
    value="EpicoPI1Legado"
)

if not label:
    st.warning("Informe uma label para buscar os épicos.")
    st.stop()

if st.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

jql = f"""
labels = {label} AND issuetype = Epic
"""

with st.spinner("Carregando dados do Jira..."):
    issues, epic_map, epic_df = fetch_issues(jql)

df = issues_to_dataframe(issues)

epic_progress = calculate_epic_progress(df)

epic_df_owner = epic_df.rename(columns={"team": "epic_owner_team"})

epic_progress = epic_progress.merge(
    epic_df_owner,
    on="epic",
    how="left"
)

epics_with_children = set(epic_progress["epic"].unique())

empty_epics = epic_df[~epic_df["epic"].isin(epics_with_children)].copy()

if not empty_epics.empty:
    empty_epics["epic_owner_team"] = empty_epics["team"]
    empty_epics["completed_items"] = 0
    empty_epics["total_items"] = 0
    empty_epics["progress"] = 0.0

    epic_progress = pd.concat(
        [epic_progress, empty_epics],
        ignore_index=True,
        sort=False
    )

epic_progress["completed_items"] = epic_progress["completed_items"].fillna(0).astype(int)
epic_progress["total_items"] = epic_progress["total_items"].fillna(0).astype(int)
epic_progress["progress"] = epic_progress["progress"].fillna(0.0)

team_progress = calculate_team_progress(epic_progress)

teams = sorted(team_progress["team"].dropna().unique())

selected_teams = st.sidebar.multiselect(
    "Filtrar Squads",
    teams,
    default=teams
)

filtered_epic_progress = epic_progress[
    epic_progress["team"].isin(selected_teams)
]

filtered_team_progress = team_progress[
    team_progress["team"].isin(selected_teams)
]

today = date.today()
current_year = today.year
current_quarter = get_current_quarter(today)

period_mode = st.sidebar.selectbox(
    "Período de referência",
    ["Quarter atual", "Selecionar quarter", "Período customizado"]
)

if period_mode == "Quarter atual":
    start_date, end_date = get_quarter_dates(current_year, current_quarter)
    selected_period_label = f"{current_quarter}/{current_year}"

elif period_mode == "Selecionar quarter":
    selected_year = st.sidebar.selectbox(
        "Ano",
        [current_year - 1, current_year, current_year + 1],
        index=1
    )

    selected_quarter = st.sidebar.selectbox(
        "Quarter",
        ["Q1", "Q2", "Q3", "Q4"],
        index=["Q1", "Q2", "Q3", "Q4"].index(current_quarter)
    )

    start_date, end_date = get_quarter_dates(selected_year, selected_quarter)
    selected_period_label = f"{selected_quarter}/{selected_year}"

else:
    custom_start = st.sidebar.date_input(
        "Data inicial",
        value=date(current_year, 1, 1)
    )
    custom_end = st.sidebar.date_input(
        "Data final",
        value=today
    )

    start_date = custom_start
    end_date = custom_end
    selected_period_label = f"{start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}"

if start_date >= end_date:
    st.sidebar.error("A data final deve ser maior que a data inicial.")
    st.stop()

cluster_progress = calculate_cluster_progress(filtered_team_progress)
quarter_time_progress = calculate_quarter_time_progress(start_date, end_date)

squads_at_risk, epics_at_risk, total_epics = calculate_risk_metrics(
    filtered_epic_progress,
    filtered_team_progress,
    quarter_time_progress
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Progresso de Épicos", f"{cluster_progress:.1f}%")
col2.metric("% Tempo decorrido", f"{quarter_time_progress:.1f}%")
#col2.caption(f"Período: {selected_period_label}")
#col3.metric("Potenciais squads em risco", squads_at_risk)
col3.metric("Épicos com risco sinalizado", f"{epics_at_risk} / {total_epics}")

st.caption("⏱️ Dados atualizados a cada 5 minutos")

render_teams(
    filtered_team_progress,
    filtered_epic_progress,
    epic_map,
    df
)
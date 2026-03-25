import streamlit as st
from domain.workflow_rules import is_in_progress, is_in_approval

def render_teams(team_progress, epic_progress, epic_map, df):

    for _, team in team_progress.iterrows():

        team_name = team["team"]
        team_percent = team["progress"]

        st.subheader(f"{team_name} — {team_percent:.1f}%")

        team_epics = epic_progress[
            epic_progress["team"] == team_name
        ].sort_values("progress")

        for _, epic in team_epics.iterrows():

            epic_key = epic["epic"]
            epic_name = epic_map.get(epic_key, "")

            done = int(epic["completed_items"])
            total = int(epic["total_items"])
            progress = float(epic["progress"])
            
            is_epic_at_risk = bool(epic.get("epic_risk", False))
            epic_risk_reason = epic.get("epic_risk_reason", "")

            epic_items = df[
                (df["epic"] == epic_key) &
                (df["team"] == team_name)
            ]

            is_empty_epic = total == 0
            is_completed = done == total and total > 0

            epic_owner_team = epic.get("epic_owner_team", team_name)

            team_label = ""
            if epic_owner_team != team_name:
                team_label = f" [{epic_owner_team}]"

            epic_url = f"https://medcel.atlassian.net/browse/{epic_key}"

            risk_label = " 🚨 Risco Sinalizado" if is_epic_at_risk else ""
            
            if is_completed:
                epic_title = f"""
                <span style="font-size:18px; font-weight:700; color:#2e7d32;">
                <a href="{epic_url}" target="_blank">{epic_key}</a>
                - {epic_name} ({done}/{total}){team_label} ✅ 100% {risk_label}
                </span>
                """
            else:
                epic_title = f"""
                <span style="font-size:18px; font-weight:600;">
                <a href="{epic_url}" target="_blank">{epic_key}</a>
                - {epic_name} ({done}/{total}){team_label} {risk_label}
                </span>
                """

            st.markdown(epic_title, unsafe_allow_html=True)

            if is_empty_epic:
                st.caption("📝 Este épico ainda não possui histórias cadastradas")
            else:
                done_count = epic_items[epic_items["done"] == 1].shape[0]

                in_approval_count = epic_items[
                    epic_items["status"].apply(is_in_approval)
                ].shape[0]

                in_progress_count = epic_items[
                    epic_items["status"].apply(is_in_progress)
                ].shape[0]

                todo_count = epic_items.shape[0] - done_count - in_progress_count - in_approval_count

                st.markdown(
                    f"✅ **CONCLUÍDO:** {done_count} &nbsp;&nbsp; "
                    f"🟣 **EM HOMOLOGAÇÃO:** {in_approval_count} &nbsp;&nbsp; "
                    f"🔵 **EM ANDAMENTO:** {in_progress_count} &nbsp;&nbsp; "
                    f"⚪ **A FAZER:** {todo_count}"
                )

            epic_total_items = df[df["epic"] == epic_key].shape[0]
            if epic_total_items != total and total > 0:
                st.caption("📎 Épico com atividades compartilhadas")
                
            if is_epic_at_risk and epic_risk_reason:
                st.caption(f"🚨 Motivo do risco: {epic_risk_reason}")

            if not is_empty_epic:
                st.progress(progress / 100)

            blocked_count = epic_items[epic_items["flagged"] == True].shape[0]

            if blocked_count > 0:
                st.warning(f"🚧 {blocked_count} item(ns) bloqueado(s) neste épico")

            if not epic_items.empty:
                with st.expander("Ver itens do épico"):

                    epic_items_sorted = epic_items.sort_values("priority")

                    for _, item in epic_items_sorted.iterrows():

                        is_blocked = item.get("flagged", False)
                        status = item["status"]

                        if is_blocked:
                            icon = "🚧"
                        elif item["done"]:
                            icon = "✅"
                        elif is_in_approval(status):
                            icon = "🟣"
                        elif is_in_progress(status):
                            icon = "🔵"
                        else:
                            icon = "⚪"

                        issue_key = item["issue"]
                        issue_url = f"https://medcel.atlassian.net/browse/{issue_key}"

                        blocked_label = ""
                        if is_blocked:
                            blocked_label = " 🚧 **BLOQUEADO**"

                        st.markdown(
                            f"{icon} **[{issue_key}]({issue_url})** - {item['summary']}{blocked_label}  \n"
                            f"Status: `{status}`"
                        )
            elif not is_empty_epic:
                st.caption("Sem itens para exibir")

        st.divider()
import streamlit as st
import plotly.express as px
from datetime import date


def render_roadmap(roadmap_df, start_date=None, end_date=None):
    if roadmap_df.empty:
        st.info("Nenhum épico com datas válidas para exibir no roadmap.")
        return

    fig = px.timeline(
        roadmap_df,
        x_start="start_date",
        x_end="end_date",
        y="display_name",
        color="roadmap_status",
        text="progress_label",
        color_discrete_map={
            "Em andamento": "#2563eb",
            "Concluído": "#16a34a",
            "Em risco": "#dc2626",
            "Transbordo": "#7c3aed"
        },
        hover_data={
            "team": True,
            "epic_full_name": True,
            "progress_label": True,
            "date_range_label": True,
            "roadmap_status": True,
            "risk_label": True,
            "transbordo_label": True,
            "start_date": False,
            "end_date": False,
            "epic_risk": False,
            "is_transbordo": False
        }
    )
    
    fig.update_traces(textposition="inside")

    today = date.today()

    # Linha de hoje
    fig.add_vline(
        x=today,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    # Limites do quarter
    if start_date is not None:
        fig.add_vline(
            x=start_date,
            line_width=1,
            line_dash="dot",
            line_color="#6b7280"
        )

    if end_date is not None:
        fig.add_vline(
            x=end_date,
            line_width=1,
            line_dash="dot",
            line_color="#6b7280"
        )

    # Área sombreada do quarter
    if start_date is not None and end_date is not None:
        fig.add_vrect(
            x0=start_date,
            x1=end_date,
            fillcolor="#f3f4f6",
            opacity=0.2,
            line_width=0
        )

    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        height=max(600, len(roadmap_df) * 35),
        xaxis_title="Timeline",
        yaxis_title="Épicos",
        legend_title="Status",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
from datetime import date, timedelta

import streamlit as st

from streamlit_app.client import FinHealthClient
from streamlit_app.config import DEFAULT_DAYS, MARKETPLACES

st.set_page_config(
    page_title="FinHealth SMB",
    page_icon="📊",
    layout="wide",
)


def _init_session_state() -> None:
    if "from_date" not in st.session_state:
        today = date.today()
        st.session_state["from_date"] = today - timedelta(days=DEFAULT_DAYS)
        st.session_state["to_date"] = today
        st.session_state["marketplace"] = "ALL"


def _render_sidebar(client: FinHealthClient) -> None:
    st.sidebar.title("FinHealth SMB")

    from_date = st.sidebar.date_input(
        "Период с",
        value=st.session_state["from_date"],
        key="sidebar_from_date",
    )
    to_date = st.sidebar.date_input(
        "Период по",
        value=st.session_state["to_date"],
        key="sidebar_to_date",
    )
    st.session_state["from_date"] = from_date
    st.session_state["to_date"] = to_date

    marketplace_index = MARKETPLACES.index(
        st.session_state.get("marketplace", "ALL")
    )
    marketplace = st.sidebar.selectbox(
        "Маркетплейс",
        options=MARKETPLACES,
        index=marketplace_index,
        key="sidebar_marketplace",
    )
    st.session_state["marketplace"] = marketplace

    st.sidebar.divider()

    alerts = client.get_alerts(from_date, to_date)
    alert_count = len(alerts)
    if alert_count > 0:
        st.sidebar.error(f"🔴 {alert_count} алертов")
    else:
        st.sidebar.success("✅ Нет алертов")


_init_session_state()
_client = FinHealthClient()
_render_sidebar(_client)

st.title("FinHealth SMB")
st.info("Выберите страницу в боковом меню.")

from datetime import date, timedelta

import streamlit as st

from streamlit_app.client import FinHealthClient
from streamlit_app.components.alert_badge import render_alert
from streamlit_app.config import DEFAULT_DAYS

st.set_page_config(page_title="Alerts - FinHealth", layout="wide")


def _ensure_session_state() -> None:
    if "from_date" not in st.session_state:
        today = date.today()
        st.session_state["from_date"] = today - timedelta(days=DEFAULT_DAYS)
        st.session_state["to_date"] = today


def _severity_rank(severity: str) -> int:
    if severity == "critical":
        return 0
    if severity == "warning":
        return 1
    return 2


_ensure_session_state()

from_date: date = st.session_state["from_date"]
to_date: date = st.session_state["to_date"]

st.title("Алерты")
st.caption(f"Период: {from_date} — {to_date}")

client = FinHealthClient()

with st.spinner("Загрузка алертов..."):
    alerts = client.get_alerts(from_date, to_date)

critical_count = sum(1 for a in alerts if a.get("severity") == "critical")
warning_count = sum(1 for a in alerts if a.get("severity") == "warning")

col_critical, col_warning = st.columns(2)
with col_critical:
    st.metric(label="🔴 Критических", value=critical_count)
with col_warning:
    st.metric(label="🟡 Предупреждений", value=warning_count)

st.divider()

if not alerts:
    st.success("✅ Всё в порядке — нет активных алертов")
else:
    sorted_alerts = sorted(
        alerts,
        key=lambda a: _severity_rank(a.get("severity", "warning")),
    )
    for alert in sorted_alerts:
        render_alert(alert)

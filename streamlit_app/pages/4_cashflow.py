import pandas as pd
import streamlit as st

from streamlit_app.client import FinHealthClient
from streamlit_app.components.charts import build_cashflow_bar_chart
from streamlit_app.components.metric_card import render_metric


def _format_money(value: float) -> str:
    amount = int(round(float(value)))
    return f"₽ {amount:,}"


def _format_signed_money(value: float) -> str:
    sign = "+" if float(value) >= 0 else "-"
    amount = int(round(abs(float(value))))
    return f"{sign}₽ {amount:,}"


st.set_page_config(page_title="ДДС - FinHealth", layout="wide")
st.title("Денежный поток (ДДС)")

if "from_date" not in st.session_state or "to_date" not in st.session_state:
    st.warning("Откройте главную страницу для выбора периода.")
    st.stop()

from_date = st.session_state["from_date"]
to_date = st.session_state["to_date"]

client = FinHealthClient()
with st.spinner("Загрузка..."):
    data = client.get_cashflow(from_date, to_date)

if not data:
    st.info("Нет данных за выбранный период")
    st.stop()

entries: list[dict] = list(data.get("entries", []) or [])
gaps: list[dict] = list(data.get("gaps", []) or [])

total_inflow = sum(
    float(e.get("amount", 0) or 0)
    for e in entries
    if float(e.get("amount", 0) or 0) > 0
)
total_outflow = sum(
    float(e.get("amount", 0) or 0)
    for e in entries
    if float(e.get("amount", 0) or 0) < 0
)
net_cash = float(data.get("net_cash", total_inflow + total_outflow))

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Поступления", _format_money(total_inflow))
with col2:
    render_metric("Списания", _format_money(abs(total_outflow)))
with col3:
    render_metric(
        "Чистый поток",
        _format_money(net_cash),
        delta=_format_signed_money(net_cash),
    )
with col4:
    render_metric("Кассовых разрывов", str(len(gaps)))

st.divider()

if entries:
    figure = build_cashflow_bar_chart(entries)
    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )
else:
    st.info("Нет данных за выбранный период")

st.divider()

if gaps:
    st.subheader("Кассовые разрывы")
    for gap in gaps:
        gap_start = gap.get("gap_start", "")
        gap_end = gap.get("gap_end", "")
        days = gap.get("days", 0)
        st.warning(
            f"⚠️ Разрыв {gap_start} → {gap_end}: {days} дней без выплат"
        )

st.subheader("Записи ДДС")
if entries:
    rows = [
        {
            "Дата": e.get("entry_date", ""),
            "Маркетплейс": e.get("marketplace", ""),
            "Тип": e.get("entry_type", ""),
            "Сумма (₽)": _format_signed_money(e.get("amount", 0) or 0),
        }
        for e in sorted(entries, key=lambda x: str(x.get("entry_date", "")))
    ]
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Нет данных за выбранный период")

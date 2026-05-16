import pandas as pd
import streamlit as st

from streamlit_app.client import FinHealthClient
from streamlit_app.components.charts import build_pnl_bar_chart
from streamlit_app.components.metric_card import render_metric


def _format_money(value: float) -> str:
    amount = int(round(float(value)))
    return f"₽ {amount:,}"


st.set_page_config(page_title="P&L - FinHealth", layout="wide")
st.title("P&L — Прибыль и убытки")

if "from_date" not in st.session_state or "to_date" not in st.session_state:
    st.warning("Откройте главную страницу для выбора периода.")
    st.stop()

from_date = st.session_state["from_date"]
to_date = st.session_state["to_date"]
marketplace_filter = st.session_state.get("marketplace", "ALL")
marketplace_param: str | None = (
    None if marketplace_filter == "ALL" else marketplace_filter
)

client = FinHealthClient()
with st.spinner("Загрузка..."):
    data = client.get_pnl(from_date, to_date, marketplace_param)

if not data:
    st.info("Нет данных за выбранный период")
    st.stop()

gross_profit = float(data.get("gross_profit", 0))
net_profit = float(data.get("net_profit", 0))
total_revenue = float(data.get("total_revenue", 0))
total_commissions = float(data.get("total_commissions", 0))
total_logistics = float(data.get("total_logistics", 0))
total_returns = float(data.get("total_returns", 0))
total_ad_spend = float(data.get("total_ad_spend", 0))
total_cogs = float(data.get("total_cogs", 0))

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Валовая прибыль", _format_money(gross_profit))
with col2:
    render_metric("Чистая прибыль", _format_money(net_profit))
with col3:
    render_metric("Выручка", _format_money(total_revenue))
with col4:
    render_metric("Рекламные расходы", _format_money(total_ad_spend))

st.divider()

figure = build_pnl_bar_chart(data)
st.plotly_chart(
    figure,
    use_container_width=True,
    config={"displayModeBar": False},
)

st.divider()

st.subheader("Сводка P&L")
rows = [
    {"Статья": "Выручка", "Сумма (₽)": _format_money(total_revenue)},
    {"Статья": "Комиссии", "Сумма (₽)": _format_money(total_commissions)},
    {"Статья": "Логистика", "Сумма (₽)": _format_money(total_logistics)},
    {"Статья": "Возвраты", "Сумма (₽)": _format_money(total_returns)},
    {"Статья": "Реклама", "Сумма (₽)": _format_money(total_ad_spend)},
    {"Статья": "Себестоимость", "Сумма (₽)": _format_money(total_cogs)},
    {"Статья": "Валовая прибыль", "Сумма (₽)": _format_money(gross_profit)},
    {"Статья": "Чистая прибыль", "Сумма (₽)": _format_money(net_profit)},
]

dataframe = pd.DataFrame(rows)


def _highlight_totals(row: pd.Series) -> list[str]:
    if row["Статья"] == "Чистая прибыль":
        return ["background-color: #1DB954; color: white; font-weight: bold"] * len(row)
    if row["Статья"] == "Валовая прибыль":
        return ["font-weight: bold"] * len(row)
    return [""] * len(row)


styled = dataframe.style.apply(_highlight_totals, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

import pandas as pd
import streamlit as st

from streamlit_app.client import FinHealthClient
from streamlit_app.components.charts import build_profit_line_chart
from streamlit_app.components.metric_card import render_metric


def _format_money(value: float) -> str:
    amount = int(round(float(value)))
    return f"₽ {amount:,}".replace(",", ",")


def _format_percent(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def _format_profit_delta(value: float) -> str:
    sign = "+" if float(value) >= 0 else "-"
    amount = int(round(abs(float(value))))
    return f"{sign}₽ {amount:,}"


st.set_page_config(page_title="Дашборд - FinHealth", layout="wide")
st.title("Дашборд")

if "from_date" not in st.session_state or "to_date" not in st.session_state:
    st.warning("Откройте главную страницу для выбора периода.")
    st.stop()

from_date = st.session_state["from_date"]
to_date = st.session_state["to_date"]

client = FinHealthClient()
with st.spinner("Загрузка..."):
    data = client.get_dashboard(from_date, to_date)

if not data:
    st.info("Нет данных за выбранный период")
    st.stop()

revenue = float(data.get("total_revenue", 0))
net_profit = float(data.get("net_profit", 0))
margin = float(data.get("margin", 0))
commission_share = float(data.get("commission_share", 0))

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Выручка", _format_money(revenue))
with col2:
    render_metric(
        "Чистая прибыль",
        _format_money(net_profit),
        delta=_format_profit_delta(net_profit),
    )
with col3:
    render_metric("Маржа", _format_percent(margin))
with col4:
    render_metric("Доля комиссий", _format_percent(commission_share))

st.divider()

daily_profits = data.get("daily_profits", [])
if daily_profits:
    figure = build_profit_line_chart(daily_profits)
    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )
else:
    st.info("Нет данных за выбранный период")

st.divider()

st.subheader("Топ SKU по прибыли")
top_skus = data.get("top_skus", [])
if top_skus:
    rows = [
        {
            "Товар": sku.get("name", ""),
            "Маркетплейс": sku.get("marketplace", ""),
            "Выручка": _format_money(sku.get("revenue", 0)),
            "Прибыль": _format_money(sku.get("profit", 0)),
            "Маржа": _format_percent(sku.get("margin", 0)),
        }
        for sku in top_skus[:10]
    ]
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Нет данных за выбранный период")

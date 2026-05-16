from typing import Any

import streamlit as st

from streamlit_app.client import FinHealthClient
from streamlit_app.components.charts import build_waterfall_chart


def _format_money(value: float) -> str:
    amount = int(round(float(value)))
    return f"₽ {amount:,}"


def _format_percent(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def _return_rate(sku: dict[str, Any]) -> float:
    revenue = float(sku.get("revenue", 0) or 0)
    returns = float(sku.get("returns", 0) or 0)
    if revenue <= 0:
        return 0.0
    return returns / revenue


def _sort_key(sku: dict[str, Any], field: str) -> float:
    if field == "margin":
        return float(sku.get("margin", 0) or 0)
    if field == "roi":
        return float(sku.get("roi", 0) or 0)
    return float(sku.get("profit", 0) or 0)


def _render_sku_card(sku: dict[str, Any]) -> None:
    name = str(sku.get("name", ""))
    marketplace = str(sku.get("marketplace", ""))
    revenue = float(sku.get("revenue", 0) or 0)
    profit = float(sku.get("profit", 0) or 0)
    margin = float(sku.get("margin", 0) or 0)
    roi = float(sku.get("roi", 0) or 0)
    ret_rate = _return_rate(sku)

    header = f"**{name}**  \n`{marketplace}`"
    body = (
        f"Выручка: **{_format_money(revenue)}**  \n"
        f"Прибыль: **{_format_money(profit)}**  \n"
        f"Маржа: **{_format_percent(margin)}**  \n"
        f"ROI: **{_format_percent(roi)}**  \n"
        f"Процент возвратов: **{_format_percent(ret_rate)}**"
    )
    container = st.error if profit < 0 else st.success
    container(f"{header}\n\n{body}")


st.set_page_config(page_title="Юнит-экономика - FinHealth", layout="wide")
st.title("Юнит-экономика")

if "from_date" not in st.session_state or "to_date" not in st.session_state:
    st.warning("Откройте главную страницу для выбора периода.")
    st.stop()

from_date = st.session_state["from_date"]
to_date = st.session_state["to_date"]

client = FinHealthClient()
with st.spinner("Загрузка..."):
    skus = client.get_unit_economics(from_date, to_date)

if not skus:
    st.info("Нет данных за выбранный период")
    st.stop()

col_search, col_sort = st.columns([2, 1])
with col_search:
    query = st.text_input("Поиск SKU", value="", placeholder="Название товара")
with col_sort:
    sort_field = st.selectbox("Сортировка", ["profit", "margin", "roi"])

filtered: list[dict[str, Any]] = [
    sku
    for sku in skus
    if query.strip().lower() in str(sku.get("name", "")).lower()
]
filtered.sort(key=lambda item: _sort_key(item, sort_field), reverse=True)

st.divider()

if not filtered:
    st.info("Нет SKU, удовлетворяющих фильтру")
    st.stop()

st.subheader(f"Разбивка по SKU ({len(filtered)})")

for index in range(0, len(filtered), 2):
    left, right = st.columns(2)
    with left:
        _render_sku_card(filtered[index])
    if index + 1 < len(filtered):
        with right:
            _render_sku_card(filtered[index + 1])

st.divider()

st.subheader("Разбивка затрат")
name_to_sku: dict[str, dict[str, Any]] = {
    str(sku.get("name", "")): sku for sku in filtered
}
selected_name = st.selectbox(
    "Выберите SKU для разбивки",
    list(name_to_sku.keys()),
)
if selected_name:
    figure = build_waterfall_chart(name_to_sku[selected_name])
    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )

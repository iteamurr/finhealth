import streamlit as st


def render_alert(alert: dict) -> None:
    color = "🔴" if alert["severity"] == "critical" else "🟡"
    sku_info = f" — SKU: {alert['sku_id']}" if alert.get("sku_id") else ""
    value_info = (
        f" ({alert['value']})" if alert.get("value") is not None else ""
    )
    st.markdown(
        f"{color} **{alert['message']}**{sku_info}{value_info}"
    )

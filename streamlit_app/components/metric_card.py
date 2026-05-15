import streamlit as st


def render_metric(
    label: str, value: str, delta: str | None = None
) -> None:
    # обертка метрики с единым форматом
    st.metric(label=label, value=value, delta=delta)

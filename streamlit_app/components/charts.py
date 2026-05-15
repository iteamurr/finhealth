from collections import defaultdict
from typing import Any

import plotly.graph_objects as go

from streamlit_app.config import COLOR_LOSS, COLOR_OZON, COLOR_PROFIT, COLOR_WB

_MARKETPLACE_COLORS: dict[str, str] = {
    "WB": COLOR_WB,
    "OZON": COLOR_OZON,
}


def build_profit_line_chart(daily_profits: list[dict]) -> go.Figure:
    # ежедневная чистая прибыль по маркетплейсам
    by_mp: dict[str, list[tuple[Any, float]]] = defaultdict(list)
    for item in daily_profits:
        marketplace = str(item.get("marketplace", "")).upper()
        by_mp[marketplace].append(
            (item.get("date"), float(item.get("profit", 0)))
        )

    figure = go.Figure()
    for marketplace, points in by_mp.items():
        points.sort(key=lambda pair: pair[0])
        figure.add_trace(
            go.Scatter(
                x=[p[0] for p in points],
                y=[p[1] for p in points],
                mode="lines+markers",
                name=marketplace,
                line={
                    "color": _MARKETPLACE_COLORS.get(marketplace, "#888"),
                    "width": 2,
                },
            )
        )

    figure.update_layout(
        title="Net profit by day",
        height=350,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        xaxis_title="",
        yaxis_title="₽",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return figure


_PNL_CATEGORIES: list[tuple[str, str, str, float]] = [
    ("revenue", "Revenue", "#1DB954", 1.0),
    ("commissions", "Commissions", "#E74C3C", 1.0),
    ("logistics", "Logistics", "#F39C12", 1.0),
    ("returns", "Returns", "#E74C3C", 0.7),
    ("ad_spend", "Ad spend", "#9B59B6", 1.0),
    ("cogs", "COGS", "#95A5A6", 1.0),
]

_PNL_FIELD_MAP: dict[str, str] = {
    "revenue": "total_revenue",
    "commissions": "total_commissions",
    "logistics": "total_logistics",
    "returns": "total_returns",
    "ad_spend": "total_ad_spend",
    "cogs": "total_cogs",
}


def build_pnl_bar_chart(pnl: dict) -> go.Figure:
    # столбчатая диаграмма с разбивкой по статьям затрат
    figure = go.Figure()
    for key, label, color, opacity in _PNL_CATEGORIES:
        field = _PNL_FIELD_MAP[key]
        value = float(pnl.get(field, 0) or 0)
        figure.add_trace(
            go.Bar(
                name=label,
                x=[label],
                y=[value],
                marker={"color": color, "opacity": opacity},
                hovertemplate="%{x}: ₽ %{y:,.0f}<extra></extra>",
            )
        )

    figure.update_layout(
        title="P&L breakdown",
        barmode="stack",
        height=350,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        xaxis_title="",
        yaxis_title="₽",
        showlegend=False,
    )
    return figure


def build_waterfall_chart(sku: dict[str, Any]) -> go.Figure:
    # водопадный график разбивки затрат по SKU
    revenue = float(sku.get("revenue", 0) or 0)
    commissions = float(sku.get("commissions", 0) or 0)
    logistics = float(sku.get("logistics", 0) or 0)
    returns = float(sku.get("returns", 0) or 0)
    ad_spend = float(sku.get("ad_spend", 0) or 0)

    measures = [
        "absolute",
        "relative",
        "relative",
        "relative",
        "relative",
        "total",
    ]
    labels = [
        "Выручка",
        "Комиссии",
        "Логистика",
        "Возвраты",
        "Реклама",
        "Прибыль",
    ]
    values = [
        revenue,
        -commissions,
        -logistics,
        -returns,
        -ad_spend,
        0,
    ]

    figure = go.Figure(
        go.Waterfall(
            measure=measures,
            x=labels,
            y=values,
            connector={"line": {"color": "#888"}},
            increasing={"marker": {"color": "#1DB954"}},
            decreasing={"marker": {"color": "#E74C3C"}},
            totals={"marker": {"color": "#1DB954"}},
            hovertemplate="%{x}: ₽ %{y:,.0f}<extra></extra>",
        )
    )

    name = str(sku.get("name", ""))
    figure.update_layout(
        title=f"Разбивка затрат — {name}",
        height=350,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        xaxis_title="",
        yaxis_title="₽",
        showlegend=False,
    )
    return figure


def build_cashflow_bar_chart(entries: list[dict]) -> go.Figure:
    # таймлайн ДДС: зеленый — поступления, красный — списания
    sorted_entries = sorted(
        entries, key=lambda item: str(item.get("entry_date", ""))
    )
    dates = [item.get("entry_date") for item in sorted_entries]
    amounts = [float(item.get("amount", 0) or 0) for item in sorted_entries]
    colors = [
        COLOR_PROFIT if value >= 0 else COLOR_LOSS for value in amounts
    ]
    types = [str(item.get("entry_type", "")) for item in sorted_entries]
    marketplaces = [
        str(item.get("marketplace", "")) for item in sorted_entries
    ]

    figure = go.Figure(
        go.Bar(
            x=dates,
            y=amounts,
            marker={"color": colors},
            customdata=list(zip(types, marketplaces)),
            hovertemplate=(
                "%{x}<br>%{customdata[1]} %{customdata[0]}"
                "<br>₽ %{y:,.0f}<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="Cash flow timeline",
        height=350,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        xaxis_title="",
        yaxis_title="₽",
        showlegend=False,
        bargap=0.2,
    )
    return figure

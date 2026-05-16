"""Smoke test for FinHealthClient against a running backend.

Usage:
    Backend must be running at API_BASE_URL (default http://localhost:8000/api/v1)
    python scripts/smoke_test_frontend_client.py
"""

import sys
from datetime import date, timedelta

from streamlit_app.client.api_client import FinHealthClient
from streamlit_app.config import DEFAULT_DAYS


def _summarize(name: str, payload: object) -> None:
    if isinstance(payload, dict):
        print(f"[{name}] dict with keys: {sorted(payload.keys())}")
    elif isinstance(payload, list):
        sample_keys = sorted(payload[0].keys()) if payload else []
        print(f"[{name}] list of {len(payload)} items, sample keys: {sample_keys}")
    else:
        print(f"[{name}] unexpected type: {type(payload).__name__}")


def main() -> int:
    to_date = date.today()
    from_date = to_date - timedelta(days=DEFAULT_DAYS)
    print(f"date range: {from_date} -> {to_date}")

    client = FinHealthClient()

    dashboard = client.get_dashboard(from_date, to_date)
    _summarize("dashboard", dashboard)

    pnl_all = client.get_pnl(from_date, to_date, marketplace=None)
    _summarize("pnl(ALL)", pnl_all)

    pnl_wb = client.get_pnl(from_date, to_date, marketplace="WB")
    _summarize("pnl(WB)", pnl_wb)

    unit_econ = client.get_unit_economics(from_date, to_date)
    _summarize("unit_economics", unit_econ)

    cashflow = client.get_cashflow(from_date, to_date)
    _summarize("cashflow", cashflow)

    alerts = client.get_alerts(from_date, to_date)
    _summarize("alerts", alerts)

    return 0


if __name__ == "__main__":
    sys.exit(main())

from datetime import date
from typing import Any

import httpx
import streamlit as st

from streamlit_app.config import (
    API_BASE_URL,
    CACHE_TTL_SECONDS,
    DATE_FORMAT,
    REQUEST_TIMEOUT_SECONDS,
)


def _format_date(value: date) -> str:
    return value.strftime(DATE_FORMAT)


def _emit_error(message: str) -> None:
    try:
        st.error(message)
    except Exception:
        # вне рантайма Streamlit (смоук-тесты)
        print(f"[FinHealthClient] {message}")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _get(path: str, params: dict[str, str]) -> Any:
    url = f"{API_BASE_URL}{path}"
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except (httpx.ConnectError, httpx.TimeoutException):
        _emit_error(
            "⚠️ Backend unavailable — make sure the API is running on "
            f"{API_BASE_URL}"
        )
        return None
    except httpx.HTTPStatusError as exc:
        _emit_error(
            f"Backend error {exc.response.status_code} on {path}: "
            f"{exc.response.text}"
        )
        return None
    except httpx.RequestError as exc:
        _emit_error(f"Cannot reach backend at {url}: {exc}")
        return None


class FinHealthClient:
    def __init__(self, base_url: str = API_BASE_URL) -> None:
        self.base_url = base_url

    def get_dashboard(self, from_date: date, to_date: date) -> dict:
        params = {
            "from_date": _format_date(from_date),
            "to_date": _format_date(to_date),
        }
        data = _get("/dashboard", params)
        if not isinstance(data, dict):
            return {}
        return data

    def get_pnl(
        self,
        from_date: date,
        to_date: date,
        marketplace: str | None,
    ) -> dict:
        params: dict[str, str] = {
            "from_date": _format_date(from_date),
            "to_date": _format_date(to_date),
        }
        if marketplace is not None and marketplace.upper() != "ALL":
            params["marketplace"] = marketplace
        data = _get("/pnl", params)
        if not isinstance(data, dict):
            return {}
        return data

    def get_unit_economics(
        self, from_date: date, to_date: date
    ) -> list[dict]:
        params = {
            "from_date": _format_date(from_date),
            "to_date": _format_date(to_date),
        }
        data = _get("/unit-economics", params)
        if not isinstance(data, list):
            return []
        return data

    def get_cashflow(self, from_date: date, to_date: date) -> dict:
        params = {
            "from_date": _format_date(from_date),
            "to_date": _format_date(to_date),
        }
        data = _get("/cashflow", params)
        if not isinstance(data, dict):
            return {}
        return data

    def get_alerts(self, from_date: date, to_date: date) -> list[dict]:
        params = {
            "from_date": _format_date(from_date),
            "to_date": _format_date(to_date),
        }
        data = _get("/alerts", params)
        if not isinstance(data, list):
            return []
        return data

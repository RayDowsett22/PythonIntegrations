"""Date and integration filters shared by every dashboard page."""

import pandas as pd
import streamlit as st

from dashboard.config import DATE_WINDOWS_DAYS

TIME_PERIOD_STATE_KEY = "dashboard_time_period_selection"
TIME_PERIOD_WIDGET_KEY = "dashboard_time_period_widget"


def _save_time_period_selection() -> None:
    """Keep the selected period outside the page-scoped widget state."""
    st.session_state[TIME_PERIOD_STATE_KEY] = st.session_state[TIME_PERIOD_WIDGET_KEY]


def render_sidebar_filters(runs: pd.DataFrame) -> pd.DataFrame:
    """Render common controls and return the filtered run-history frame."""
    st.sidebar.header("Filters")
    # Streamlit may clear a widget when leaving its page, so mirror its value
    # in an ordinary session-state entry and restore it on the next page.
    default_window = next(iter(DATE_WINDOWS_DAYS))
    if st.session_state.get(TIME_PERIOD_STATE_KEY) not in DATE_WINDOWS_DAYS:
        st.session_state[TIME_PERIOD_STATE_KEY] = default_window
    if st.session_state.get(TIME_PERIOD_WIDGET_KEY) not in DATE_WINDOWS_DAYS:
        st.session_state[TIME_PERIOD_WIDGET_KEY] = st.session_state[TIME_PERIOD_STATE_KEY]

    selected_window = st.sidebar.selectbox(
        "Time period",
        list(DATE_WINDOWS_DAYS),
        key=TIME_PERIOD_WIDGET_KEY,
        on_change=_save_time_period_selection,
    )
    days = DATE_WINDOWS_DAYS[selected_window]

    filtered = runs
    if days is not None:
        now = pd.Timestamp.now()
        filtered = filtered.loc[
            filtered["StartTime"].between(now - pd.Timedelta(days=days), now)
        ]

    integrations = sorted(filtered["TaskName"].dropna().unique().tolist())
    selected_integrations = st.sidebar.multiselect(
        "Integrations", options=integrations, default=integrations
    )
    return filtered.loc[filtered["TaskName"].isin(selected_integrations)].copy()

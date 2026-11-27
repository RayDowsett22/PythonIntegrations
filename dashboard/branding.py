"""Shared Bentley-inspired visual style for Streamlit pages."""

from html import escape

import streamlit as st

NAVY = "#003B70"
BLUE = "#0079C1"
ORANGE = "#F7941D"
INK = "#263746"
MUTED = "#637381"
PAGE_BACKGROUND = "#F3F5F7"
PLOT_BACKGROUND = "#FFFFFF"


def apply_branding() -> None:
    """Apply consistent brand colors and layout details across all pages."""
    # One shared stylesheet keeps the Streamlit multipage shell visually consistent.
    st.markdown(
        """
        <style>
        :root {
            --brand-navy: #003B70;
            --brand-blue: #0079C1;
            --brand-orange: #F7941D;
            --brand-ink: #263746;
            --brand-muted: #637381;
        }
        div[data-testid="stAppViewContainer"] {
            background: #F3F5F7;
            color: var(--brand-ink);
        }
        div[data-testid="stHeader"] {
            background: rgba(243, 245, 247, 0.96);
        }
        section[data-testid="stSidebar"] {
            background: #E8EDF2;
            border-right: 1px solid #D4DDE5;
        }
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] label {
            color: var(--brand-navy);
        }
        .brand-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: -1rem 0 1.5rem;
            padding: 0.9rem 1.25rem;
            color: #FFFFFF;
            background: var(--brand-navy);
            border-bottom: 4px solid var(--brand-orange);
        }
        .brand-banner h1 {
            margin: 0;
            color: #FFFFFF;
            font-size: 1.5rem;
            line-height: 1.25;
        }
        .brand-banner p {
            margin: 0.2rem 0 0;
            color: #DCE8F2;
            font-size: 0.9rem;
        }
        .brand-wordmark {
            flex: 0 0 auto;
            color: #FFFFFF;
            font-size: 1.35rem;
            font-weight: 750;
            letter-spacing: -0.04em;
        }
        .brand-wordmark span {
            color: var(--brand-orange);
        }
        div[data-testid="stMetric"] {
            min-height: 7rem;
            padding: 1rem 1.1rem;
            background: #FFFFFF;
            border: 1px solid #D5DEE7;
            border-top: 4px solid var(--brand-blue);
            border-radius: 0.35rem;
            box-shadow: 0 1px 3px rgba(0, 35, 67, 0.07);
        }
        div[data-testid="stMetricLabel"] p {
            color: var(--brand-muted);
            font-weight: 600;
        }
        div[data-testid="stMetricValue"] {
            color: var(--brand-navy);
        }
        div[data-testid="stMarkdownContainer"] h2 {
            padding-bottom: 0.45rem;
            color: var(--brand-navy);
            border-bottom: 2px solid #D5DEE7;
        }
        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            background: #FFFFFF;
            border: 1px solid #D5DEE7;
            border-radius: 0.35rem;
        }
        div[data-testid="stDataFrame"] {
            padding: 0.25rem;
        }
        div[data-testid="stAlert"] {
            border-left-color: var(--brand-orange);
        }
        @media (max-width: 640px) {
            .brand-banner {
                align-items: flex-start;
                padding: 0.8rem;
            }
            .brand-banner h1 {
                font-size: 1.2rem;
            }
            .brand-wordmark {
                font-size: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str) -> None:
    """Render a shared navy page banner with a text-only Bentley wordmark."""
    st.markdown(
        f"""
        <header class="brand-banner">
            <div>
                <h1>{escape(title)}</h1>
                <p>{escape(subtitle)}</p>
            </div>
            <div class="brand-wordmark" aria-label="Bentley">Bentley<span>.</span></div>
        </header>
        """,
        unsafe_allow_html=True,
    )

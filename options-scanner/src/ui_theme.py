"""Trader-terminal UI theme for the Streamlit options scanner.

A small toolkit that gives the app a Bloomberg-Terminal-Lite aesthetic:
deep slate background, gold signal accent, monospace tabular numbers,
dense rows, semantic bull/bear/neutral coloring with glyph fallbacks.

Public entry points:
    inject_theme()         -- global CSS, fonts, scrollbars, sidebar.
    status_bar(...)        -- top trader-style status row.
    status_footer(...)     -- bottom data-source / timestamp band.
    kpi_chip(...)          -- compact stat tile (label / value / delta).
    pill(text, tone)       -- inline tone-tagged badge.
    divider(label)         -- thin labeled divider.
    data_table(df, **opts) -- st.dataframe wrapper with tabular-num defaults.
    altair_theme()         -- shared dict for charts (font, gridlines, BG).
    chart_palette          -- semantic color tokens for chart marks.
    spinner_text(stage)    -- trader-flavored loading copy.
    empty_state(title, hint) -- terminal-tone empty placeholder.

All number cells render in JetBrains Mono with tabular-nums + right
alignment. Bull/bear/neutral always pair color with a Unicode glyph
(▲ ▼ ●) so color is never the sole signal.
"""

from __future__ import annotations

from datetime import datetime
from textwrap import dedent
from typing import Any, Iterable

import streamlit as st

# ── Tokens ───────────────────────────────────────────────────────────────────

PRIMARY      = "#F59E0B"   # signal gold
PRIMARY_FG   = "#0F172A"
SECONDARY    = "#FBBF24"
ACCENT       = "#8B5CF6"   # rare — highlights only
BG           = "#0F172A"   # deep slate
FG           = "#F8FAFC"
CARD         = "#222735"
CARD_FG      = "#F8FAFC"
MUTED        = "#272F42"
MUTED_FG     = "#94A3B8"
BORDER       = "#334155"
BULL         = "#22C55E"   # positive residual
BEAR         = "#EF4444"   # negative residual
NEUTRAL      = "#94A3B8"
RING         = "#F59E0B"
WARN         = "#F59E0B"

GLYPH_UP     = "▲"    # ▲
GLYPH_DOWN   = "▼"    # ▼
GLYPH_DOT    = "●"    # ●
GLYPH_REC    = "▬"    # ▬ (em-dash-ish bar for neutral row markers)

FONT_SANS = (
    '"Inter", -apple-system, BlinkMacSystemFont, "SF Pro Text", '
    '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
)
FONT_MONO = (
    '"JetBrains Mono", "SF Mono", ui-monospace, "IBM Plex Mono", '
    '"Roboto Mono", Menlo, Consolas, monospace'
)


# ── Tone helpers ─────────────────────────────────────────────────────────────

def _tone_color(tone: str) -> str:
    """Map a semantic tone keyword to a token color."""
    return {
        "bull":    BULL,
        "bear":    BEAR,
        "warn":    WARN,
        "neutral": NEUTRAL,
        "info":    NEUTRAL,
        "gold":    PRIMARY,
        "accent":  ACCENT,
        "muted":   MUTED_FG,
    }.get(tone, NEUTRAL)


def _tone_glyph(tone: str) -> str:
    """Map a tone to its Unicode marker glyph."""
    return {
        "bull": GLYPH_UP,
        "bear": GLYPH_DOWN,
        "warn": GLYPH_DOT,
    }.get(tone, GLYPH_DOT)


# ── Global CSS injection ─────────────────────────────────────────────────────

def inject_theme() -> None:
    """Inject the terminal theme — fonts, palette, sidebar, tables, buttons.

    Call once near the top of the Streamlit script, after st.set_page_config.
    Idempotent: re-running on a rerun is safe (Streamlit replaces the markup).
    """
    st.html(
        dedent(f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {{
            --tx-bg:      {BG};
            --tx-fg:      {FG};
            --tx-card:    {CARD};
            --tx-card-fg: {CARD_FG};
            --tx-muted:   {MUTED};
            --tx-muted-fg:{MUTED_FG};
            --tx-border:  {BORDER};
            --tx-primary: {PRIMARY};
            --tx-bull:    {BULL};
            --tx-bear:    {BEAR};
            --tx-accent:  {ACCENT};
            --tx-ring:    {RING};
            --tx-font-sans: {FONT_SANS};
            --tx-font-mono: {FONT_MONO};
        }}

        html, body, [data-testid="stAppViewContainer"], .main {{
            background-color: var(--tx-bg) !important;
            color: var(--tx-fg);
            font-family: var(--tx-font-sans);
            font-feature-settings: "cv11", "ss01", "ss03";
        }}

        [data-testid="stHeader"] {{
            background-color: var(--tx-bg);
            border-bottom: 1px solid var(--tx-border);
            backdrop-filter: blur(6px);
        }}

        /* Tighten the global page rhythm. */
        .block-container {{
            padding-top: 0.5rem !important;
            padding-bottom: 4rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            max-width: 100% !important;
        }}

        /* ── Typography ───────────────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
            font-family: var(--tx-font-sans);
            color: var(--tx-fg);
            letter-spacing: -0.01em;
            font-weight: 600;
        }}
        h1 {{ font-size: 1.5rem;  margin: 0.4rem 0 0.6rem; }}
        h2 {{ font-size: 1.15rem; margin: 0.3rem 0 0.5rem; }}
        h3 {{ font-size: 1.0rem;  margin: 0.3rem 0 0.4rem; }}
        h4 {{ font-size: 0.9rem;  margin: 0.2rem 0 0.3rem; }}

        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li,
        .stCaption, [data-testid="stCaptionContainer"], small,
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
        label[data-testid="stWidgetLabel"] {{
            color: var(--tx-fg);
            font-family: var(--tx-font-sans);
        }}
        .stCaption, [data-testid="stCaptionContainer"], small {{
            color: var(--tx-muted-fg);
            font-size: 0.78rem;
        }}

        /* Widget labels: uppercase tiny-caps trader vibe */
        [data-testid="stWidgetLabel"] p {{
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--tx-muted-fg);
        }}

        /* ── Sidebar ──────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {{
            background-color: #161B26 !important;
            border-right: 1px solid var(--tx-border);
        }}
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            color: var(--tx-muted-fg);
        }}
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown span,
        [data-testid="stSidebar"] .stMarkdown li,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {{
            color: var(--tx-fg);
        }}

        /* Section header inside the sidebar — uppercase tiny caps */
        .tx-rail-section {{
            font-family: var(--tx-font-sans);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.68rem;
            font-weight: 700;
            color: var(--tx-muted-fg);
            border-top: 1px solid var(--tx-border);
            padding: 0.85rem 0 0.35rem;
            margin: 0.4rem 0 0.4rem;
        }}
        .tx-rail-section:first-of-type {{
            border-top: none;
            padding-top: 0.25rem;
        }}

        /* ── Inputs ───────────────────────────────────────────────────── */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        textarea {{
            background-color: var(--tx-card) !important;
            color: var(--tx-fg) !important;
            border-color: var(--tx-border) !important;
            border-radius: 6px !important;
            font-family: var(--tx-font-mono) !important;
            font-variant-numeric: tabular-nums;
            font-size: 0.86rem !important;
        }}
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            font-family: var(--tx-font-sans) !important;
        }}
        /* Numeric-only inputs (Streamlit's stNumberInput) right-aligned. */
        [data-testid="stNumberInput"] input {{
            text-align: right;
        }}
        /* Tighter step buttons */
        [data-testid="stNumberInput"] button {{
            background-color: var(--tx-muted) !important;
            color: var(--tx-fg) !important;
            border-color: var(--tx-border) !important;
        }}

        /* Focus rings: 3px gold instead of default. */
        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stDateInput"] input:focus,
        textarea:focus,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within,
        button:focus-visible,
        .stButton > button:focus-visible {{
            outline: 3px solid var(--tx-ring) !important;
            outline-offset: 1px;
            border-color: var(--tx-ring) !important;
        }}

        /* ── Buttons ─────────────────────────────────────────────────── */
        .stButton > button,
        .stDownloadButton > button {{
            background-color: var(--tx-card);
            color: var(--tx-fg);
            border: 1px solid var(--tx-border);
            border-radius: 6px;
            font-family: var(--tx-font-sans);
            font-weight: 500;
            font-size: 0.82rem;
            letter-spacing: 0.02em;
            min-height: 38px;
            transition: background-color 120ms ease, border-color 120ms ease;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            background-color: #2D3447;
            border-color: var(--tx-muted-fg);
            color: var(--tx-fg);
        }}

        /* Primary action — gold. Override Streamlit's dynamic green/blue. */
        .stButton > button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background-color: var(--tx-primary) !important;
            color: #0F172A !important;
            border-color: var(--tx-primary) !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
        }}
        .stButton > button[kind="primary"] p,
        button[data-testid="stBaseButton-primary"] p {{
            color: #0F172A !important;
        }}
        .stButton > button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover {{
            background-color: #FBBF24 !important;
            border-color: #FBBF24 !important;
            color: #0F172A !important;
        }}

        /* ── Containers / cards ───────────────────────────────────────── */
        [data-testid="stContainer"][class*="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: var(--tx-card);
            border: 1px solid var(--tx-border) !important;
            border-radius: 8px !important;
        }}

        /* ── Tabs ─────────────────────────────────────────────────────── */
        [data-testid="stTabs"] [role="tablist"] {{
            border-bottom: 1px solid var(--tx-border);
            gap: 0.25rem;
        }}
        [data-testid="stTabs"] [role="tab"] {{
            font-family: var(--tx-font-sans);
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.1em;
            font-weight: 600;
            color: var(--tx-muted-fg);
            padding: 0.55rem 0.9rem;
            border-bottom: 2px solid transparent;
        }}
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
            color: var(--tx-primary);
            border-bottom-color: var(--tx-primary);
        }}
        [data-testid="stTabs"] [role="tab"] p {{
            color: inherit;
            font-size: inherit;
            font-weight: inherit;
        }}

        /* ── Dividers ─────────────────────────────────────────────────── */
        [data-testid="stDivider"] hr {{
            border-color: var(--tx-border);
            margin: 0.25rem 0 !important;
        }}

        /* ── Metrics (built-in) ──────────────────────────────────────── */
        [data-testid="stMetric"] {{
            background: var(--tx-card);
            border: 1px solid var(--tx-border);
            border-radius: 8px;
            padding: 0.55rem 0.75rem;
        }}
        [data-testid="stMetricLabel"] {{
            color: var(--tx-muted-fg) !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.7rem !important;
            font-weight: 600;
        }}
        [data-testid="stMetricValue"] {{
            font-family: var(--tx-font-mono) !important;
            font-variant-numeric: tabular-nums;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: var(--tx-fg);
        }}
        [data-testid="stMetricDelta"] {{
            font-family: var(--tx-font-mono) !important;
            font-variant-numeric: tabular-nums;
        }}

        /* ── Tables / dataframe ──────────────────────────────────────── */
        [data-testid="stDataFrame"] {{
            background: var(--tx-card);
            border: 1px solid var(--tx-border);
            border-radius: 8px;
        }}
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="columnheader"] span,
        [data-testid="stDataFrame"] [role="columnheader"] div {{
            font-family: var(--tx-font-sans) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            font-size: 0.7rem !important;
            font-weight: 700 !important;
            color: var(--tx-muted-fg) !important;
            background-color: #1B2030 !important;
        }}
        [data-testid="stDataFrame"] [role="row"] [role="gridcell"] {{
            font-family: var(--tx-font-mono) !important;
            font-variant-numeric: tabular-nums !important;
            font-size: 0.82rem !important;
            color: var(--tx-fg) !important;
        }}
        /* Row hover for scannability */
        [data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {{
            background-color: rgba(245, 158, 11, 0.06) !important;
        }}

        /* ── Status bar (top) ────────────────────────────────────────── */
        .tx-status {{
            display: flex;
            align-items: stretch;
            gap: 0;
            background: var(--tx-card);
            border: 1px solid var(--tx-border);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 0.85rem;
        }}
        .tx-status__cell {{
            flex: 1 1 0;
            padding: 0.55rem 0.85rem;
            border-right: 1px solid var(--tx-border);
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
            min-width: 0;
        }}
        .tx-status__cell:last-child {{ border-right: none; }}
        .tx-status__cell--anchor {{
            background: linear-gradient(90deg,
                rgba(245, 158, 11, 0.12),
                rgba(245, 158, 11, 0.0));
            flex: 0 0 auto;
            min-width: 9rem;
        }}
        .tx-status__label {{
            font-family: var(--tx-font-sans);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.65rem;
            font-weight: 700;
            color: var(--tx-muted-fg);
        }}
        .tx-status__value {{
            font-family: var(--tx-font-mono);
            font-variant-numeric: tabular-nums;
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--tx-fg);
            white-space: nowrap;
        }}
        .tx-status__value--big {{
            font-size: 1.35rem;
        }}
        .tx-status__delta {{
            font-family: var(--tx-font-mono);
            font-variant-numeric: tabular-nums;
            font-size: 0.78rem;
            font-weight: 500;
        }}
        .tx-status__delta--bull {{ color: var(--tx-bull); }}
        .tx-status__delta--bear {{ color: var(--tx-bear); }}
        .tx-status__delta--neutral {{ color: var(--tx-muted-fg); }}

        /* ── KPI chip ─────────────────────────────────────────────────── */
        .tx-chip {{
            background: var(--tx-card);
            border: 1px solid var(--tx-border);
            border-radius: 8px;
            padding: 0.65rem 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            min-height: 70px;
        }}
        .tx-chip__label {{
            font-family: var(--tx-font-sans);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.65rem;
            font-weight: 700;
            color: var(--tx-muted-fg);
        }}
        .tx-chip__value {{
            font-family: var(--tx-font-mono);
            font-variant-numeric: tabular-nums;
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--tx-fg);
            line-height: 1.15;
        }}
        .tx-chip__delta {{
            font-family: var(--tx-font-mono);
            font-variant-numeric: tabular-nums;
            font-size: 0.78rem;
            font-weight: 500;
        }}
        .tx-chip--bull   .tx-chip__delta {{ color: var(--tx-bull); }}
        .tx-chip--bear   .tx-chip__delta {{ color: var(--tx-bear); }}
        .tx-chip--warn   .tx-chip__delta {{ color: var(--tx-primary); }}
        .tx-chip--neutral .tx-chip__delta {{ color: var(--tx-muted-fg); }}
        .tx-chip--bull   {{ border-left: 3px solid var(--tx-bull); }}
        .tx-chip--bear   {{ border-left: 3px solid var(--tx-bear); }}
        .tx-chip--warn   {{ border-left: 3px solid var(--tx-primary); }}
        .tx-chip--accent {{ border-left: 3px solid var(--tx-accent); }}

        /* ── Pill ─────────────────────────────────────────────────────── */
        .tx-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            font-family: var(--tx-font-mono);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            line-height: 1.5;
            border: 1px solid var(--tx-border);
            background: var(--tx-muted);
            color: var(--tx-fg);
            white-space: nowrap;
        }}
        .tx-pill--bull {{ color: var(--tx-bull);    border-color: rgba(34,197,94,0.45); background: rgba(34,197,94,0.10); }}
        .tx-pill--bear {{ color: var(--tx-bear);    border-color: rgba(239,68,68,0.45); background: rgba(239,68,68,0.10); }}
        .tx-pill--gold {{ color: var(--tx-primary); border-color: rgba(245,158,11,0.5);  background: rgba(245,158,11,0.10); }}
        .tx-pill--accent {{ color: var(--tx-accent); border-color: rgba(139,92,246,0.5);  background: rgba(139,92,246,0.10); }}
        .tx-pill--muted {{ color: var(--tx-muted-fg); }}

        /* ── Section divider ─────────────────────────────────────────── */
        .tx-div {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin: 1rem 0 0.5rem;
            color: var(--tx-muted-fg);
            font-family: var(--tx-font-sans);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.7rem;
            font-weight: 700;
        }}
        .tx-div::before,
        .tx-div::after {{
            content: "";
            flex: 1;
            height: 1px;
            background: var(--tx-border);
        }}

        /* ── Empty state ─────────────────────────────────────────────── */
        .tx-empty {{
            text-align: center;
            padding: 2.5rem 1.25rem;
            border: 1px dashed var(--tx-border);
            border-radius: 8px;
            background: rgba(34, 39, 53, 0.45);
            color: var(--tx-muted-fg);
            font-family: var(--tx-font-sans);
        }}
        .tx-empty__title {{
            color: var(--tx-fg);
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
            letter-spacing: 0.04em;
        }}
        .tx-empty__hint {{
            font-size: 0.82rem;
            line-height: 1.45;
            max-width: 36rem;
            margin: 0 auto;
        }}

        /* ── Status footer ──────────────────────────────────────────── */
        .tx-footer {{
            display: flex;
            flex-wrap: wrap;
            gap: 1.25rem;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0.85rem;
            margin-top: 1.5rem;
            border-top: 1px solid var(--tx-border);
            font-family: var(--tx-font-mono);
            font-variant-numeric: tabular-nums;
            color: var(--tx-muted-fg);
            font-size: 0.72rem;
            letter-spacing: 0.04em;
        }}
        .tx-footer__left {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
        .tx-footer__right {{ display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; }}
        .tx-footer .tx-led {{
            display: inline-block;
            width: 7px; height: 7px;
            border-radius: 999px;
            background: var(--tx-bull);
            box-shadow: 0 0 6px var(--tx-bull);
            margin-right: 0.4rem;
        }}
        .tx-footer .tx-led--bear {{
            background: var(--tx-bear);
            box-shadow: 0 0 6px var(--tx-bear);
        }}
        .tx-footer .tx-led--gold {{
            background: var(--tx-primary);
            box-shadow: 0 0 6px var(--tx-primary);
        }}

        /* ── Expander ────────────────────────────────────────────────── */
        [data-testid="stExpander"] details {{
            background: var(--tx-card);
            border: 1px solid var(--tx-border) !important;
            border-radius: 8px;
        }}
        [data-testid="stExpander"] summary {{
            font-family: var(--tx-font-sans);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--tx-fg);
        }}

        /* ── Progress / alerts / sliders ─────────────────────────────── */
        [data-testid="stProgress"] > div > div > div {{
            background-color: var(--tx-primary) !important;
        }}
        [data-testid="stAlert"] {{
            background-color: var(--tx-card);
            border: 1px solid var(--tx-border);
            color: var(--tx-fg);
            border-radius: 8px;
        }}

        [data-testid="stSlider"] [role="slider"] {{
            background-color: var(--tx-primary) !important;
            border-color: var(--tx-primary) !important;
        }}
        [data-testid="stSlider"] [data-baseweb="slider"] div[role="progressbar"] {{
            background-color: var(--tx-primary) !important;
        }}

        /* ── Radio / checkbox dark BG ───────────────────────────────── */
        [data-testid="stRadio"] label,
        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label p,
        [data-testid="stCheckbox"] label p {{
            color: var(--tx-fg) !important;
        }}

        /* ── Scrollbar ───────────────────────────────────────────────── */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: var(--tx-bg); }}
        ::-webkit-scrollbar-thumb {{
            background: var(--tx-muted);
            border-radius: 999px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--tx-border); }}

        /* ── File uploader ───────────────────────────────────────────── */
        [data-testid="stFileUploader"] section {{
            background-color: var(--tx-card);
            border-color: var(--tx-border);
            color: var(--tx-fg);
        }}

        /* ── Reduced motion ──────────────────────────────────────────── */
        @media (prefers-reduced-motion: reduce) {{
            * {{ transition: none !important; animation: none !important; }}
        }}

        /* ── Selection highlight ─────────────────────────────────────── */
        ::selection {{
            background: rgba(245, 158, 11, 0.35);
            color: var(--tx-fg);
        }}
        </style>
        """)
    )


# ── Status bar (top) ─────────────────────────────────────────────────────────

def _status_cell(label: str, value: str, delta: str | None = None,
                 tone: str = "neutral", anchor: bool = False,
                 big: bool = False) -> str:
    delta_html = ""
    if delta:
        delta_html = (
            f'<div class="tx-status__delta tx-status__delta--{tone}">'
            f'{delta}</div>'
        )
    big_cls = " tx-status__value--big" if big else ""
    anchor_cls = " tx-status__cell--anchor" if anchor else ""
    return (
        f'<div class="tx-status__cell{anchor_cls}">'
        f'  <div class="tx-status__label">{label}</div>'
        f'  <div class="tx-status__value{big_cls}">{value}</div>'
        f'  {delta_html}'
        f'</div>'
    )


def status_bar(cells: Iterable[dict[str, Any]]) -> None:
    """Render a trader-style status bar row.

    `cells` is an iterable of dicts with keys:
        label, value, delta (optional), tone (bull/bear/neutral), anchor, big.

    The first cell is typically the ticker; pass anchor=True to highlight it
    with a subtle gold-tinted gradient (the "anchor" cell of the bar).
    """
    html = ['<div class="tx-status">']
    for c in cells:
        html.append(_status_cell(
            label=str(c.get("label", "")),
            value=str(c.get("value", "")),
            delta=c.get("delta"),
            tone=c.get("tone", "neutral"),
            anchor=bool(c.get("anchor", False)),
            big=bool(c.get("big", False)),
        ))
    html.append("</div>")
    st.markdown("\n".join(html), unsafe_allow_html=True)


# ── KPI chip ────────────────────────────────────────────────────────────────

def kpi_chip(label: str, value: str, delta: str | None = None,
             tone: str = "neutral") -> str:
    """Return the HTML for one KPI chip. Render with st.markdown(..., unsafe_allow_html=True).

    Args:
        label: Uppercase caption, e.g. "SPOT" or "NEXT EARN".
        value: Primary numeric value as a pre-formatted string.
        delta: Optional secondary line, e.g. "+2.1%" or "in 5d".
        tone:  bull / bear / warn / accent / neutral — sets the left border
               and delta color.
    """
    delta_html = (f'<div class="tx-chip__delta">{delta}</div>'
                  if delta else "")
    return (
        f'<div class="tx-chip tx-chip--{tone}">'
        f'  <div class="tx-chip__label">{label}</div>'
        f'  <div class="tx-chip__value">{value}</div>'
        f'  {delta_html}'
        f'</div>'
    )


def kpi_row(chips: Iterable[str]) -> None:
    """Render a row of `kpi_chip(...)` HTML strings as a CSS grid."""
    items = list(chips)
    if not items:
        return
    grid = (
        f'<div style="display:grid; '
        f'grid-template-columns: repeat({len(items)}, minmax(0, 1fr)); '
        f'gap: 0.65rem; margin-bottom: 0.85rem;">'
        + "".join(items)
        + "</div>"
    )
    st.markdown(grid, unsafe_allow_html=True)


# ── Pill ────────────────────────────────────────────────────────────────────

def pill(text: str, tone: str = "muted") -> str:
    """Return HTML for an inline pill badge with a tone glyph.

    `tone` ∈ bull, bear, gold, accent, muted, warn. Color is paired with a
    Unicode glyph so the signal works without color (▲ for bull, ▼ for
    bear, ● otherwise).
    """
    glyph_map = {
        "bull": GLYPH_UP, "bear": GLYPH_DOWN,
        "gold": "◆",     # ◆
        "accent": "◆",
        "warn": "▲",
    }
    glyph = glyph_map.get(tone, GLYPH_DOT)
    return f'<span class="tx-pill tx-pill--{tone}">{glyph} {text}</span>'


# ── Divider ─────────────────────────────────────────────────────────────────

def divider(label: str | None = None) -> None:
    """Render a thin labeled divider, e.g. "VOLATILITY SURFACE"."""
    if label:
        st.markdown(f'<div class="tx-div">{label}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<hr style="border:0; border-top:1px solid '
                    'var(--tx-border); margin: 0.5rem 0;" />',
                    unsafe_allow_html=True)


# ── Data table wrapper ──────────────────────────────────────────────────────

def data_table(df, **opts) -> Any:
    """Thin st.dataframe wrapper with terminal defaults.

    Passes through any kwargs (column_config, hide_index, etc.). Sets
    width="stretch" by default.
    """
    opts.setdefault("hide_index", True)
    opts.setdefault("width", "stretch")
    return st.dataframe(df, **opts)


# ── Empty state ─────────────────────────────────────────────────────────────

def empty_state(title: str, hint: str = "") -> None:
    """Render a terminal-tone empty placeholder."""
    st.markdown(
        f'<div class="tx-empty">'
        f'  <div class="tx-empty__title">{title}</div>'
        f'  <div class="tx-empty__hint">{hint}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Spinner copy ────────────────────────────────────────────────────────────

_SPINNER_COPY = {
    "chain":    "scanning chain…",
    "surface":  "fitting surface…",
    "spreads":  "building spreads…",
    "earnings": "checking earnings calendar…",
    "roll":     "looking up close cost…",
    "portfolio":"scanning portfolio…",
}


def spinner_text(stage: str, suffix: str = "") -> str:
    """Return a trader-flavored spinner label."""
    base = _SPINNER_COPY.get(stage, f"{stage}…")
    return f"{base} {suffix}".rstrip()


# ── Status footer ──────────────────────────────────────────────────────────

def status_footer(provider_label: str, scan_ts_str: str,
                  tone: str = "neutral", extra: str = "") -> None:
    """Render the bottom status band: data source · timestamp · last refresh.

    `tone` controls the LED color (bull=green, bear=red, gold=signal-gold,
    neutral=muted).
    """
    led_class = "" if tone == "bull" else f" tx-led--{tone}"
    now_str = datetime.now().strftime("%H:%M:%S")
    extra_html = (f'<span>{extra}</span>' if extra else "")
    st.markdown(
        f'<div class="tx-footer">'
        f'  <div class="tx-footer__left">'
        f'    <span><span class="tx-led{led_class}"></span>'
        f'          SRC {provider_label.upper()}</span>'
        f'    <span>SCAN {scan_ts_str or "—"}</span>'
        f'  </div>'
        f'  <div class="tx-footer__right">'
        f'    {extra_html}'
        f'    <span>UI {now_str}</span>'
        f'    <span style="color: var(--tx-primary); font-weight:700;">'
        f'      STOCKPILE / OPTIONS</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Altair chart theming ───────────────────────────────────────────────────

chart_palette = {
    "bg":      BG,
    "card":    CARD,
    "fg":      FG,
    "muted":   MUTED_FG,
    "grid":    MUTED,
    "border":  BORDER,
    "bull":    BULL,
    "bear":    BEAR,
    "primary": PRIMARY,
    "accent":  ACCENT,
    "neutral": NEUTRAL,
}


def altair_theme() -> dict:
    """Altair config dict matching the terminal aesthetic.

    Apply via:
        alt.themes.register("terminal", lambda: {"config": altair_theme()})
        alt.themes.enable("terminal")
    """
    return {
        "background": BG,
        "view": {
            "stroke": BORDER,
            "fill": CARD,
        },
        "title": {
            "color": FG,
            "subtitleColor": MUTED_FG,
            "font": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            "subtitleFont": "Inter, sans-serif",
            "fontSize": 14,
            "fontWeight": 600,
            "anchor": "start",
        },
        "axis": {
            "domain": False,
            "tickColor": BORDER,
            "labelColor": MUTED_FG,
            "titleColor": MUTED_FG,
            "gridColor": MUTED,
            "gridOpacity": 0.55,
            "labelFont": ("JetBrains Mono, SF Mono, ui-monospace, "
                          "monospace"),
            "titleFont": "Inter, sans-serif",
            "labelFontSize": 10,
            "titleFontSize": 11,
            "titleFontWeight": 600,
            "labelFontWeight": 400,
        },
        "axisX": {"titlePadding": 8},
        "axisY": {"titlePadding": 8},
        "legend": {
            "labelColor": FG,
            "titleColor": MUTED_FG,
            "labelFont": "Inter, sans-serif",
            "titleFont": "Inter, sans-serif",
            "labelFontSize": 10,
            "titleFontSize": 10,
            "symbolType": "circle",
            "padding": 6,
        },
        "header": {
            "labelColor": FG,
            "titleColor": MUTED_FG,
        },
        "range": {
            "category": [PRIMARY, BULL, BEAR, ACCENT, "#FBBF24",
                         "#94A3B8", "#22D3EE"],
            "diverging": [BEAR, "#94A3B8", BULL],
        },
    }


def register_altair_theme() -> None:
    """Register and enable the terminal Altair theme. Idempotent."""
    import altair as alt
    alt.themes.register("terminal", lambda: {"config": altair_theme()})
    alt.themes.enable("terminal")

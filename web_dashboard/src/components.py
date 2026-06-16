from __future__ import annotations

import json
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from src.formatting import tidy_dataframe


def set_global_styles() -> None:
    dark_mode = bool(st.session_state.get("dark_theme_enabled", False))
    theme_vars = """
        :root {
            --dashboard-primary: #2f5fda;
            --dashboard-bg: #f7f9fd;
            --dashboard-surface: #f3f6fb;
            --dashboard-card-bg: #ffffff;
            --dashboard-text: #101828;
            --dashboard-muted: #667085;
            --dashboard-border: rgba(47, 95, 218, 0.20);
            --dashboard-border-muted: rgba(152, 162, 179, 0.36);
            --dashboard-shadow: rgba(16, 24, 40, 0.07);
            --dashboard-control-bg: #ffffff;
            --dashboard-control-hover: #eef4ff;
            --dashboard-control-selected: #e5edff;
            --dashboard-control-text: #101828;
            --dashboard-control-muted: #667085;
            --dashboard-success: #168a69;
            --dashboard-warning: #b86b0b;
            --dashboard-danger: #c24150;
            --dashboard-cyan: #0f7f8f;
        }
    """
    if dark_mode:
        theme_vars = """
        :root {
            --dashboard-primary: #7aa2ff;
            --dashboard-bg: #08111f;
            --dashboard-surface: #101827;
            --dashboard-card-bg: #121c2f;
            --dashboard-text: #e7edf7;
            --dashboard-muted: #9aa8bd;
            --dashboard-border: rgba(122, 162, 255, 0.30);
            --dashboard-border-muted: rgba(154, 168, 189, 0.22);
            --dashboard-shadow: rgba(0, 0, 0, 0.35);
            --dashboard-control-bg: #0f172a;
            --dashboard-control-hover: #17233a;
            --dashboard-control-selected: #1d3158;
            --dashboard-control-text: #e7edf7;
            --dashboard-control-muted: #b7c3d6;
            --dashboard-success: #4fd1a5;
            --dashboard-warning: #f2b44b;
            --dashboard-danger: #fb7185;
            --dashboard-cyan: #38bdf8;
        }
        """

    st.markdown(
        "<style>\n" + theme_vars + """
        .stApp {
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--dashboard-primary) 7%, var(--dashboard-bg)) 0%,
                    var(--dashboard-bg) 36%
                );
            color: var(--dashboard-text);
        }
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
            background: transparent;
        }
        .block-container {
            max-width: 1760px;
            padding: 1.35rem clamp(1rem, 1.35vw, 1.75rem) 2.5rem;
            width: 100%;
            color: var(--dashboard-text);
        }
        [data-testid="stSidebar"] {
            background: var(--dashboard-surface);
            border-right: 1px solid var(--dashboard-border-muted);
            flex: 0 0 286px !important;
            height: 100vh !important;
            max-width: 286px !important;
            min-width: 286px !important;
            overflow: hidden !important;
            position: sticky !important;
            resize: none !important;
            top: 0 !important;
            width: 286px !important;
        }
        [data-testid="stSidebar"]::after {
            content: "";
            cursor: default;
            height: 100vh;
            left: 279px;
            pointer-events: auto;
            position: fixed;
            top: 0;
            width: 14px;
            z-index: 999999;
        }
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebar"] [data-testid="stSidebarContent"],
        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            max-width: 286px !important;
            min-width: 286px !important;
            overflow: hidden !important;
            resize: none !important;
            width: 286px !important;
        }
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] *::before,
        [data-testid="stSidebar"] *::after {
            scrollbar-width: none !important;
        }
        [data-testid="stSidebar"] *::-webkit-scrollbar {
            display: none !important;
            height: 0 !important;
            width: 0 !important;
        }
        [data-testid="stSidebarResizer"],
        [data-testid="stSidebarResizeHandle"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebar"] + div[role="separator"],
        [data-testid="stSidebar"] ~ div[role="separator"],
        div[role="separator"][aria-orientation="vertical"] {
            display: none !important;
            pointer-events: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            display: flex;
            min-height: calc(100vh - 3rem);
            gap: 0.64rem;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-weight: 750;
        }
        .sidebar-brand {
            align-items: center;
            display: grid;
            gap: 0.72rem;
            grid-template-columns: 48px minmax(0, 1fr);
            margin: 0.05rem 0 1.05rem;
            padding: 0 0 1rem;
            position: relative;
        }
        .sidebar-brand::after {
            background: linear-gradient(90deg, var(--dashboard-primary), transparent 72%);
            border-radius: 999px;
            bottom: 0;
            content: "";
            height: 2px;
            left: 0;
            position: absolute;
            width: 78%;
        }
        .sidebar-logo {
            align-items: center;
            background:
                radial-gradient(circle at 28% 22%, rgba(255, 255, 255, 0.55), transparent 32%),
                linear-gradient(135deg, #2f5fda 0%, #0f7f8f 62%, #168a69 100%);
            border: 1px solid color-mix(in srgb, var(--dashboard-primary) 40%, transparent);
            border-radius: 14px;
            box-shadow: 0 12px 28px color-mix(in srgb, var(--dashboard-primary) 18%, transparent);
            display: inline-flex;
            height: 48px;
            justify-content: center;
            overflow: hidden;
            position: relative;
            width: 48px;
        }
        .sidebar-logo svg {
            display: block;
            height: 34px;
            width: 34px;
        }
        .sidebar-logo::after {
            background: rgba(255, 255, 255, 0.26);
            border-radius: 999px;
            content: "";
            height: 9px;
            position: absolute;
            right: 8px;
            top: 8px;
            width: 9px;
        }
        .sidebar-brand-copy {
            min-width: 0;
        }
        .sidebar-brand-name {
            color: var(--dashboard-text);
            font-size: 1.55rem;
            font-weight: 900;
            letter-spacing: 0;
            line-height: 1.02;
        }
        .sidebar-brand-tagline {
            color: var(--dashboard-muted);
            font-size: 0.76rem;
            font-weight: 720;
            line-height: 1.25;
            margin-top: 0.24rem;
        }
        .sidebar-footer-spacer {
            flex: 1 1 auto;
            min-height: clamp(3rem, 18vh, 14rem);
        }
        .sidebar-theme-footer {
            border-top: 1px solid var(--dashboard-border-muted);
            margin-top: 0.4rem;
            padding-top: 0.85rem;
        }
        [data-testid="stSidebar"] [data-testid="stToggle"] {
            border-top: 1px solid var(--dashboard-border-muted);
            margin-top: 0.5rem;
            padding-top: 0.85rem;
        }
        [data-testid="stSidebar"] [data-testid="stToggle"] label,
        [data-testid="stSidebar"] [data-testid="stToggle"] p {
            color: var(--dashboard-text) !important;
            font-weight: 700;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.42rem;
            width: 100%;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
            align-items: center;
            border: 1px solid transparent;
            border-radius: 14px;
            box-sizing: border-box;
            cursor: pointer;
            display: flex;
            margin: 0.10rem 0;
            min-height: 58px;
            overflow: hidden;
            padding: 0.82rem 1rem 0.82rem 1.35rem;
            position: relative;
            transition:
                background-color 160ms ease,
                border-color 160ms ease,
                box-shadow 160ms ease,
                transform 160ms ease;
            width: 100%;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]::before {
            background: var(--dashboard-primary);
            border-radius: 999px;
            bottom: 12px;
            content: "";
            left: 0.62rem;
            opacity: 0;
            position: absolute;
            top: 12px;
            transform: scaleY(0.35);
            transition: opacity 160ms ease, transform 160ms ease;
            width: 4px;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]::after {
            background: linear-gradient(90deg, color-mix(in srgb, var(--dashboard-primary) 16%, transparent), transparent 84%);
            content: "";
            inset: 0;
            opacity: 0;
            position: absolute;
            transform: translateX(-12px);
            transition: opacity 180ms ease, transform 180ms ease;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:hover {
            background: color-mix(in srgb, var(--dashboard-primary) 8%, var(--dashboard-surface));
            border-color: color-mix(in srgb, var(--dashboard-primary) 34%, transparent);
            box-shadow: 0 12px 26px color-mix(in srgb, var(--dashboard-primary) 12%, transparent);
            transform: translateX(3px);
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:hover::before,
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:hover::after,
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked)::before,
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked)::after {
            opacity: 1;
            transform: scaleY(1);
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
            background: color-mix(in srgb, var(--dashboard-primary) 16%, var(--dashboard-surface));
            border-color: color-mix(in srgb, var(--dashboard-primary) 48%, transparent);
            box-shadow: 0 12px 26px color-mix(in srgb, var(--dashboard-primary) 14%, transparent);
            transform: translateX(0);
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] p {
            color: var(--dashboard-text);
            font-size: 1.12rem;
            font-weight: 650;
            line-height: 1.2;
            position: relative;
            transition: color 160ms ease, font-weight 160ms ease;
            z-index: 1;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p {
            color: var(--dashboard-primary);
            font-weight: 750;
        }
        [data-testid="stSidebar"] hr {
            border-color: var(--dashboard-border-muted);
        }
        @media (prefers-reduced-motion: reduce) {
            [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"],
            .metric-card {
                transition: none;
            }
        }
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"],
        section.main [data-testid="stRadio"] div[role="radiogroup"],
        .main [data-testid="stRadio"] div[role="radiogroup"] {
            align-items: stretch;
            background: var(--dashboard-control-bg) !important;
            border: 1px solid var(--dashboard-border-muted);
            border-radius: 10px;
            display: grid !important;
            gap: 0 !important;
            grid-auto-columns: minmax(0, 1fr);
            grid-auto-flow: column;
            overflow: hidden;
            width: 100%;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"],
        section.main [data-testid="stRadio"] label[data-baseweb="radio"],
        .main [data-testid="stRadio"] label[data-baseweb="radio"],
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"],
        section.main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"],
        .main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"] {
            align-items: center;
            background: var(--dashboard-control-bg) !important;
            border: 0 !important;
            border-right: 1px solid var(--dashboard-border-muted) !important;
            border-radius: 0 !important;
            box-sizing: border-box;
            cursor: pointer;
            display: flex;
            justify-content: center;
            margin: 0 !important;
            min-height: 44px;
            padding: 0.62rem 0.72rem !important;
            transition:
                background-color 150ms ease,
                color 150ms ease,
                box-shadow 150ms ease;
            width: 100%;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"]:last-child,
        section.main [data-testid="stRadio"] label[data-baseweb="radio"]:last-child,
        .main [data-testid="stRadio"] label[data-baseweb="radio"]:last-child,
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:last-child,
        section.main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:last-child,
        .main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:last-child {
            border-right: 0 !important;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child,
        section.main [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child,
        .main [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"] *,
        section.main [data-testid="stRadio"] label[data-baseweb="radio"] *,
        .main [data-testid="stRadio"] label[data-baseweb="radio"] *,
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"] *,
        section.main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"] *,
        .main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"] * {
            background: transparent !important;
            color: var(--dashboard-control-text) !important;
            opacity: 1 !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover,
        section.main [data-testid="stRadio"] label[data-baseweb="radio"]:hover,
        .main [data-testid="stRadio"] label[data-baseweb="radio"]:hover,
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:hover,
        section.main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:hover,
        .main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:hover {
            background: var(--dashboard-control-hover) !important;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
        section.main [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
        .main [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"],
        section.main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"],
        .main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"] {
            background: var(--dashboard-control-selected) !important;
            box-shadow: inset 0 0 0 1px var(--dashboard-primary);
        }
        [data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) *,
        section.main [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) *,
        .main [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) *,
        [data-testid="stMain"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"] *,
        section.main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"] *,
        .main [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"] * {
            color: var(--dashboard-primary) !important;
            font-weight: 750 !important;
            -webkit-text-fill-color: var(--dashboard-primary) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] {
            align-items: stretch !important;
            background: var(--dashboard-control-bg) !important;
            border: 1px solid var(--dashboard-border-muted) !important;
            border-radius: 10px !important;
            display: grid !important;
            gap: 0 !important;
            grid-auto-columns: minmax(0, 1fr) !important;
            grid-auto-flow: column !important;
            overflow: hidden !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"],
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label[data-baseweb="radio"] {
            align-items: center !important;
            background: var(--dashboard-control-bg) !important;
            border: 0 !important;
            border-right: 1px solid var(--dashboard-border-muted) !important;
            border-radius: 0 !important;
            box-sizing: border-box !important;
            color: var(--dashboard-control-text) !important;
            cursor: pointer !important;
            display: flex !important;
            justify-content: center !important;
            margin: 0 !important;
            min-height: 44px !important;
            padding: 0.62rem 0.72rem !important;
            width: 100% !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label:last-child,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:last-child {
            border-right: 0 !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label *,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"] *,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label[data-baseweb="radio"] * {
            color: var(--dashboard-control-text) !important;
            opacity: 1 !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"]:hover,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
            background: var(--dashboard-control-hover) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked),
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"],
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
            background: var(--dashboard-control-selected) !important;
            box-shadow: inset 0 0 0 1px var(--dashboard-primary) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) *,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] div[role="radiogroup"] [role="radio"][aria-checked="true"] *,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) * {
            color: var(--dashboard-primary) !important;
            font-weight: 750 !important;
            -webkit-text-fill-color: var(--dashboard-primary) !important;
        }
        [data-testid="stSegmentedControl"] button {
            background: var(--dashboard-control-bg) !important;
            border-color: var(--dashboard-border-muted) !important;
            border-radius: 10px;
            color: var(--dashboard-control-text) !important;
            min-height: 44px;
            opacity: 1 !important;
            transition:
                background-color 150ms ease,
                border-color 150ms ease,
                color 150ms ease,
                transform 150ms ease;
        }
        [data-testid="stSegmentedControl"] button *,
        [data-testid="stSegmentedControl"] button:disabled,
        [data-testid="stSegmentedControl"] button:disabled * {
            color: var(--dashboard-control-text) !important;
            opacity: 1 !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        [data-testid="stSegmentedControl"] button:hover {
            background: var(--dashboard-control-hover) !important;
            border-color: color-mix(in srgb, var(--dashboard-primary) 48%, var(--dashboard-border-muted)) !important;
            color: var(--dashboard-control-text) !important;
            transform: translateY(-1px);
        }
        [data-testid="stSegmentedControl"] button[aria-pressed="true"],
        [data-testid="stSegmentedControl"] button[aria-selected="true"],
        [data-testid="stSegmentedControl"] button[data-selected="true"],
        [data-testid="stSegmentedControl"] button:has(input:checked) {
            background: var(--dashboard-control-selected) !important;
            border-color: var(--dashboard-primary) !important;
            box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--dashboard-primary) 28%, transparent);
            color: var(--dashboard-primary) !important;
            font-weight: 750;
        }
        [data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
        [data-testid="stSegmentedControl"] button[aria-selected="true"] *,
        [data-testid="stSegmentedControl"] button[data-selected="true"] *,
        [data-testid="stSegmentedControl"] button:has(input:checked) * {
            color: var(--dashboard-primary) !important;
            -webkit-text-fill-color: var(--dashboard-primary) !important;
        }
        [data-testid="stButton"] button,
        [data-testid="stFormSubmitButton"] button {
            background: var(--dashboard-control-bg) !important;
            border-color: var(--dashboard-border-muted) !important;
            border-radius: 10px;
            color: var(--dashboard-control-text) !important;
            min-height: 44px;
            transition:
                background-color 150ms ease,
                border-color 150ms ease,
                box-shadow 150ms ease,
                color 150ms ease,
                transform 150ms ease;
        }
        [data-testid="stButton"] button *,
        [data-testid="stFormSubmitButton"] button * {
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        [data-testid="stButton"] button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background: var(--dashboard-control-hover) !important;
            border-color: color-mix(in srgb, var(--dashboard-primary) 34%, var(--dashboard-border-muted));
            box-shadow: 0 8px 20px color-mix(in srgb, var(--dashboard-primary) 10%, transparent);
            color: var(--dashboard-control-text) !important;
            transform: translateY(-1px);
        }
        [data-testid="stSelectbox"] [data-baseweb="select"],
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stDateInput"] [data-baseweb="input"],
        [data-testid="stDateInput"] [data-baseweb="input"] > div,
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stNumberInput"] [data-baseweb="input"],
        [data-testid="stNumberInput"] [data-baseweb="input"] > div {
            background: var(--dashboard-control-bg) !important;
            border-color: var(--dashboard-border-muted) !important;
            color: var(--dashboard-control-text) !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-testid="stDateInput"] [data-baseweb="input"] *,
        [data-testid="stTextInput"] [data-baseweb="input"] *,
        [data-testid="stNumberInput"] [data-baseweb="input"] *,
        [data-testid="stSelectbox"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            background: transparent !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        select,
        select option,
        select optgroup {
            background: var(--dashboard-control-bg) !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"]:hover,
        [data-testid="stDateInput"] [data-baseweb="input"]:hover,
        [data-testid="stTextInput"] [data-baseweb="input"]:hover,
        [data-testid="stNumberInput"] [data-baseweb="input"]:hover {
            border-color: color-mix(in srgb, var(--dashboard-primary) 42%, var(--dashboard-border-muted)) !important;
        }
        body [data-baseweb="popover"],
        body [data-baseweb="popover"] > div,
        body [data-baseweb="popover"] div,
        body [data-baseweb="popover"] [role="dialog"],
        body [data-baseweb="popover"] [role="listbox"],
        body [data-baseweb="popover"] ul,
        body [data-baseweb="popover"] li,
        body [data-baseweb="menu"],
        body [data-baseweb="menu"] div,
        body [data-baseweb="menu"] ul,
        body [data-baseweb="menu"] li,
        body [data-baseweb="select-dropdown"],
        body [data-baseweb="select-dropdown"] div,
        body [data-baseweb="select-dropdown"] ul,
        body [data-baseweb="select-dropdown"] li,
        body [data-baseweb="calendar"],
        body [data-baseweb="calendar"] > div,
        body [data-baseweb="calendar"] div,
        body [data-baseweb="calendar"] table,
        body [data-baseweb="calendar"] thead,
        body [data-baseweb="calendar"] tbody,
        body [data-baseweb="calendar"] tr,
        body [data-baseweb="calendar"] th,
        body [data-baseweb="calendar"] td {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
            border-color: var(--dashboard-border-muted) !important;
            color: var(--dashboard-text) !important;
        }
        body [data-baseweb="popover"] *,
        body [data-baseweb="menu"] *,
        body [data-baseweb="select-dropdown"] *,
        body [data-baseweb="calendar"] *,
        body [role="listbox"] *,
        body [role="option"] * {
            color: var(--dashboard-text) !important;
            -webkit-text-fill-color: var(--dashboard-text) !important;
        }
        body [data-baseweb="popover"] svg,
        body [data-baseweb="menu"] svg,
        body [data-baseweb="select-dropdown"] svg,
        body [data-baseweb="calendar"] svg {
            color: var(--dashboard-text) !important;
            fill: var(--dashboard-text) !important;
        }
        body [role="option"],
        body [data-baseweb="menu"] [role="option"],
        body [data-baseweb="popover"] [role="option"],
        body [data-baseweb="select-dropdown"] [role="option"] {
            background: var(--dashboard-card-bg) !important;
            color: var(--dashboard-text) !important;
            -webkit-text-fill-color: var(--dashboard-text) !important;
            min-height: 36px;
        }
        body [role="option"]:hover,
        body [role="option"][aria-selected="true"],
        body [role="option"][aria-current="true"],
        body [data-highlighted="true"],
        body [data-baseweb="menu"] [role="option"]:hover,
        body [data-baseweb="popover"] [role="option"]:hover,
        body [data-baseweb="select-dropdown"] [role="option"]:hover,
        body [data-baseweb="select-dropdown"] [role="option"][aria-selected="true"] {
            background: var(--dashboard-control-hover) !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        body [data-baseweb="calendar"] button,
        body [data-baseweb="calendar"] [role="button"],
        body [data-baseweb="calendar"] [role="gridcell"],
        body [data-baseweb="calendar"] [role="columnheader"] {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
            color: var(--dashboard-text) !important;
            -webkit-text-fill-color: var(--dashboard-text) !important;
        }
        body [data-baseweb="calendar"] button:hover,
        body [data-baseweb="calendar"] [role="gridcell"]:hover,
        body [data-baseweb="calendar"] [aria-selected="true"],
        body [data-baseweb="calendar"] [aria-current="date"] {
            background: var(--dashboard-control-selected) !important;
            background-color: var(--dashboard-control-selected) !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        body [data-baseweb="calendar"] [aria-selected="true"],
        body [data-baseweb="calendar"] [aria-selected="true"] *,
        body [data-baseweb="calendar"] [aria-current="date"],
        body [data-baseweb="calendar"] [aria-current="date"] * {
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        body [data-baseweb="calendar"] [aria-disabled="true"],
        body [data-baseweb="calendar"] [disabled] {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
            color: var(--dashboard-muted) !important;
            opacity: 0.48 !important;
            -webkit-text-fill-color: var(--dashboard-muted) !important;
        }
        body [data-baseweb="calendar"] {
            border: 1px solid var(--dashboard-border-muted) !important;
            border-radius: 12px !important;
            box-shadow: 0 20px 48px var(--dashboard-shadow) !important;
            overflow: hidden !important;
        }
        body [data-baseweb="calendar"] table,
        body [data-baseweb="calendar"] thead,
        body [data-baseweb="calendar"] tbody,
        body [data-baseweb="calendar"] tr,
        body [data-baseweb="calendar"] th,
        body [data-baseweb="calendar"] td {
            background: transparent !important;
            background-color: transparent !important;
            color: var(--dashboard-text) !important;
        }
        body [data-baseweb="calendar"] [role="grid"],
        body [data-baseweb="calendar"] [role="row"],
        body [data-baseweb="calendar"] [role="gridcell"],
        body [data-baseweb="calendar"] [role="gridcell"] > div,
        body [data-baseweb="calendar"] [role="gridcell"] span,
        body [data-baseweb="calendar"] [role="button"],
        body [data-baseweb="calendar"] button {
            background: transparent !important;
            background-color: transparent !important;
            color: var(--dashboard-text) !important;
            -webkit-text-fill-color: var(--dashboard-text) !important;
        }
        body [data-baseweb="calendar"] [role="gridcell"]:hover,
        body [data-baseweb="calendar"] [role="gridcell"]:hover *,
        body [data-baseweb="calendar"] button:hover,
        body [data-baseweb="calendar"] button:hover * {
            background: var(--dashboard-control-hover) !important;
            background-color: var(--dashboard-control-hover) !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        body [data-baseweb="calendar"] [aria-selected="true"],
        body [data-baseweb="calendar"] [aria-selected="true"] *,
        body [data-baseweb="calendar"] [aria-current="date"],
        body [data-baseweb="calendar"] [aria-current="date"] * {
            background: var(--dashboard-control-selected) !important;
            background-color: var(--dashboard-control-selected) !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        body [data-baseweb="calendar"] [aria-disabled="true"],
        body [data-baseweb="calendar"] [aria-disabled="true"] *,
        body [data-baseweb="calendar"] [disabled],
        body [data-baseweb="calendar"] [disabled] * {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
            color: var(--dashboard-muted) !important;
            -webkit-text-fill-color: var(--dashboard-muted) !important;
            opacity: 0.72 !important;
        }
        body [data-baseweb="calendar"] td:empty,
        body [data-baseweb="calendar"] [role="gridcell"]:empty,
        body [data-baseweb="calendar"] [role="gridcell"] > div:empty,
        body [data-baseweb="calendar"] [role="gridcell"] > span:empty,
        body [data-baseweb="calendar"] [aria-hidden="true"],
        body [data-baseweb="calendar"] [aria-hidden="true"] *,
        body [data-baseweb="calendar"] [aria-label=""],
        body [data-baseweb="calendar"] [aria-label=""] * {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
            box-shadow: none !important;
        }
        body [data-baseweb="calendar"] [role="gridcell"]::before,
        body [data-baseweb="calendar"] [role="gridcell"]::after,
        body [data-baseweb="calendar"] [role="gridcell"] > div::before,
        body [data-baseweb="calendar"] [role="gridcell"] > div::after {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
        }
        body [data-baseweb="calendar"] [aria-selected="true"]::before,
        body [data-baseweb="calendar"] [aria-selected="true"]::after,
        body [data-baseweb="calendar"] [aria-selected="true"] *::before,
        body [data-baseweb="calendar"] [aria-selected="true"] *::after {
            background: var(--dashboard-control-selected) !important;
            background-color: var(--dashboard-control-selected) !important;
        }
        [data-baseweb="popover"],
        [data-baseweb="popover"] > div,
        [data-baseweb="menu"],
        [data-baseweb="select-dropdown"],
        [data-baseweb="calendar"],
        ul[role="listbox"],
        div[role="listbox"] {
            background: var(--dashboard-card-bg) !important;
            background-color: var(--dashboard-card-bg) !important;
            border-color: var(--dashboard-border-muted) !important;
            color: var(--dashboard-text) !important;
        }
        [data-baseweb="popover"] *,
        [data-baseweb="menu"] *,
        [data-baseweb="select-dropdown"] *,
        [data-baseweb="calendar"] *,
        li[role="option"],
        div[role="option"] {
            color: var(--dashboard-text) !important;
            -webkit-text-fill-color: var(--dashboard-text) !important;
        }
        li[role="option"]:hover,
        div[role="option"]:hover,
        li[aria-selected="true"],
        div[aria-selected="true"] {
            background: var(--dashboard-control-hover) !important;
            color: var(--dashboard-control-text) !important;
            -webkit-text-fill-color: var(--dashboard-control-text) !important;
        }
        .price-chart-title {
            color: var(--dashboard-text);
            font-size: 1.06rem;
            font-weight: 780;
            line-height: 1.2;
            margin: 0 0 0.82rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--dashboard-primary) 8%, var(--dashboard-card-bg)) 0%,
                    var(--dashboard-card-bg) 70%
                );
            border-color: var(--dashboard-border-muted);
            border-radius: 10px;
            box-shadow: 0 8px 22px var(--dashboard-shadow);
        }
        [data-testid="stMetric"] {
            background: var(--dashboard-card-bg);
            border: 1px solid var(--dashboard-border-muted);
            border-top: 3px solid var(--dashboard-primary);
            border-radius: 8px;
            padding: 0.95rem 1rem;
            min-height: 112px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        }
        [data-testid="stMetricLabel"] {
            color: var(--dashboard-text);
            opacity: 0.72;
        }
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: var(--dashboard-text);
        }
        .dashboard-page-header {
            border-left: 5px solid var(--dashboard-primary);
            margin-bottom: 1.15rem;
            padding-left: 1rem;
        }
        .dashboard-page-title {
            color: var(--dashboard-text);
            font-size: clamp(2rem, 3vw, 2.8rem);
            font-weight: 800;
            line-height: 1.05;
            margin: 0 0 0.35rem;
        }
        .dashboard-page-caption {
            color: var(--dashboard-muted);
            font-size: 0.96rem;
            line-height: 1.55;
            margin: 0;
            opacity: 0.68;
        }
        .live-price-card {
            background:
                linear-gradient(
                    135deg,
                    color-mix(in srgb, var(--dashboard-primary) 8%, var(--dashboard-card-bg)) 0%,
                    var(--dashboard-card-bg) 58%
                );
            border: 1px solid color-mix(in srgb, var(--dashboard-primary) 18%, var(--dashboard-border-muted));
            border-radius: 14px;
            box-shadow: 0 16px 36px var(--dashboard-shadow);
            display: grid;
            gap: 1rem;
            grid-template-columns: minmax(0, 1fr) minmax(280px, 0.38fr);
            margin-bottom: 1rem;
            overflow: hidden;
            padding: 1.15rem 1.25rem;
            position: relative;
        }
        .live-price-card::before {
            background: var(--dashboard-primary);
            bottom: 0;
            content: "";
            left: 0;
            position: absolute;
            top: 0;
            width: 4px;
        }
        .live-price-asset {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.72rem;
            margin-bottom: 0.82rem;
        }
        .live-price-logo {
            align-items: center;
            background: #f7931a;
            border-radius: 999px;
            color: #ffffff;
            display: inline-flex;
            font-size: 1rem;
            font-weight: 850;
            height: 44px;
            justify-content: center;
            width: 44px;
        }
        .live-price-name {
            color: var(--dashboard-text);
            font-size: clamp(1.45rem, 2.1vw, 2.2rem);
            font-weight: 840;
            line-height: 1.05;
        }
        .live-price-symbol {
            color: var(--dashboard-muted);
            font-size: 1.05rem;
            font-weight: 720;
        }
        .live-price-rank,
        .live-price-status {
            align-items: center;
            background: color-mix(in srgb, var(--dashboard-primary) 9%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--dashboard-primary) 16%, transparent);
            border-radius: 999px;
            color: var(--dashboard-text);
            display: inline-flex;
            font-size: 0.8rem;
            font-weight: 780;
            min-height: 30px;
            padding: 0.2rem 0.62rem;
        }
        .live-price-status {
            background: color-mix(in srgb, var(--dashboard-success) 10%, var(--dashboard-card-bg));
            border-color: color-mix(in srgb, var(--dashboard-success) 22%, transparent);
            gap: 0.44rem;
        }
        .live-price-status-fallback {
            background: color-mix(in srgb, var(--dashboard-warning) 12%, var(--dashboard-card-bg));
            border-color: color-mix(in srgb, var(--dashboard-warning) 28%, transparent);
        }
        .live-price-dot {
            background: var(--dashboard-success);
            border-radius: 999px;
            display: inline-block;
            height: 7px;
            width: 7px;
        }
        .live-price-status-fallback .live-price-dot {
            background: var(--dashboard-warning);
        }
        .live-price-value-row {
            align-items: baseline;
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem 1rem;
            margin-bottom: 0.75rem;
        }
        .live-price-value {
            color: var(--dashboard-text);
            font-size: clamp(2.6rem, 5vw, 4.7rem);
            font-weight: 850;
            letter-spacing: 0;
            line-height: 0.96;
        }
        .live-price-change {
            border-radius: 999px;
            font-size: clamp(1rem, 1.5vw, 1.35rem);
            font-weight: 800;
            padding: 0.26rem 0.72rem;
        }
        .live-price-change-positive {
            background: color-mix(in srgb, var(--dashboard-success) 12%, var(--dashboard-card-bg));
            color: var(--dashboard-success);
        }
        .live-price-change-negative {
            background: color-mix(in srgb, var(--dashboard-danger) 12%, var(--dashboard-card-bg));
            color: var(--dashboard-danger);
        }
        .live-price-note {
            color: var(--dashboard-muted);
            font-size: 0.88rem;
            font-weight: 620;
            line-height: 1.45;
        }
        .live-price-meta-grid {
            align-self: stretch;
            display: grid;
            gap: 0.68rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .live-price-meta {
            background: color-mix(in srgb, var(--dashboard-primary) 5%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--dashboard-primary) 10%, var(--dashboard-border-muted));
            border-radius: 12px;
            min-width: 0;
            padding: 0.72rem 0.78rem;
        }
        .live-price-meta span {
            color: var(--dashboard-muted);
            display: block;
            font-size: 0.72rem;
            font-weight: 760;
            margin-bottom: 0.24rem;
        }
        .live-price-meta strong {
            color: var(--dashboard-text);
            display: block;
            font-size: 0.95rem;
            font-weight: 820;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }
        @media (max-width: 900px) {
            .live-price-card {
                grid-template-columns: 1fr;
            }
        }
        .metric-card {
            --metric-color: var(--dashboard-primary);
            --metric-tint: color-mix(in srgb, var(--metric-color) 7%, var(--dashboard-card-bg));
            background:
                linear-gradient(135deg, var(--metric-tint) 0%, var(--dashboard-card-bg) 68%);
            border: 1px solid color-mix(in srgb, var(--metric-color) 18%, var(--dashboard-border-muted));
            border-radius: 10px;
            box-shadow: 0 10px 24px var(--dashboard-shadow);
            min-height: 124px;
            overflow: hidden;
            padding: 1rem 1.05rem;
            position: relative;
            transition:
                border-color 160ms ease,
                box-shadow 160ms ease,
                transform 160ms ease;
        }
        .metric-card:hover {
            border-color: color-mix(in srgb, var(--metric-color) 32%, var(--dashboard-border-muted));
            box-shadow: 0 14px 30px var(--dashboard-shadow);
            transform: translateY(-1px);
        }
        .metric-card::before {
            background: var(--metric-color);
            bottom: 0;
            content: "";
            left: 0;
            position: absolute;
            top: 0;
            width: 4px;
        }
        .metric-card-label {
            color: var(--dashboard-text);
            font-size: 0.82rem;
            font-weight: 650;
            line-height: 1.25;
            margin-bottom: 0.55rem;
            opacity: 0.70;
            position: relative;
            z-index: 1;
        }
        .metric-card-value {
            color: var(--dashboard-text);
            font-size: clamp(1.45rem, 2.25vw, 2.15rem);
            font-weight: 780;
            line-height: 1.12;
            overflow-wrap: anywhere;
            position: relative;
            z-index: 1;
        }
        .metric-card-delta {
            background: color-mix(in srgb, var(--metric-color) 12%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--metric-color) 30%, transparent);
            border-radius: 999px;
            color: var(--dashboard-text);
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 700;
            margin-top: 0.68rem;
            padding: 0.18rem 0.55rem;
            position: relative;
            z-index: 1;
        }
        .metric-accent-blue { --metric-color: #2f5fda; }
        .metric-accent-cyan { --metric-color: #0f7f8f; }
        .metric-accent-green { --metric-color: #168a69; }
        .metric-accent-amber { --metric-color: #b86b0b; }
        .metric-accent-red { --metric-color: #c24150; }
        .metric-accent-purple { --metric-color: #6d5bd0; }
        .metric-accent-slate { --metric-color: #5b677a; }
        h1, h2, h3, h4, h5, h6, p, span, div {
            letter-spacing: 0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--dashboard-text);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--dashboard-border-muted);
            border-radius: 8px;
            overflow: hidden;
        }
        .bitrisk-table-wrap {
            background: var(--dashboard-card-bg);
            border: 1px solid var(--dashboard-border-muted);
            border-radius: 8px;
            box-shadow: 0 14px 34px var(--dashboard-shadow);
            margin: 0.25rem 0 1.15rem;
            overflow: hidden;
        }
        .bitrisk-table-scroll {
            max-height: var(--bitrisk-table-height, 420px);
            overflow: auto;
            width: 100%;
        }
        .bitrisk-table {
            border-collapse: separate;
            border-spacing: 0;
            min-width: 100%;
            width: max-content;
        }
        .bitrisk-table th,
        .bitrisk-table td {
            border-bottom: 1px solid var(--dashboard-border-muted);
            border-right: 1px solid var(--dashboard-border-muted);
            padding: 0.62rem 0.72rem;
            vertical-align: middle;
            white-space: nowrap;
        }
        .bitrisk-table th {
            background: color-mix(in srgb, var(--dashboard-control-selected) 58%, var(--dashboard-card-bg));
            color: var(--dashboard-muted);
            font-size: 0.82rem;
            font-weight: 750;
            position: sticky;
            text-align: left;
            top: 0;
            z-index: 1;
        }
        .bitrisk-table td {
            background: var(--dashboard-card-bg);
            color: var(--dashboard-text);
            font-size: 0.86rem;
            font-weight: 560;
        }
        .bitrisk-table tr:nth-child(even) td {
            background: color-mix(in srgb, var(--dashboard-control-bg) 82%, var(--dashboard-card-bg));
        }
        .bitrisk-table tr:hover td {
            background: var(--dashboard-control-hover);
        }
        .bitrisk-table th:last-child,
        .bitrisk-table td:last-child {
            border-right: 0;
        }
        .bitrisk-table tr:last-child td {
            border-bottom: 0;
        }
        .bitrisk-table .numeric-cell {
            font-variant-numeric: tabular-nums;
            text-align: right;
        }
        .small-note {
            color: var(--dashboard-muted);
            font-size: 0.92rem;
            line-height: 1.5;
            margin-top: -0.35rem;
            margin-bottom: 1.05rem;
            opacity: 0.72;
        }
        .thesis-card {
            border: 1px solid var(--dashboard-border-muted);
            border-top: 3px solid var(--dashboard-primary);
            border-radius: 8px;
            padding: 1rem 1.05rem;
            background: var(--dashboard-card-bg);
            height: 100%;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        }
        .thesis-card-label {
            color: var(--dashboard-muted);
            font-size: 0.82rem;
            margin-bottom: 0.35rem;
            opacity: 0.72;
        }
        .thesis-card-value {
            color: var(--dashboard-text);
            font-size: 1.02rem;
            font-weight: 650;
        }
        .about-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr);
            margin: 0.2rem 0 1rem;
        }
        .about-card {
            background:
                linear-gradient(
                    135deg,
                    color-mix(in srgb, var(--dashboard-primary) 6%, var(--dashboard-card-bg)) 0%,
                    var(--dashboard-card-bg) 74%
                );
            border: 1px solid var(--dashboard-border-muted);
            border-radius: 12px;
            box-shadow: 0 12px 28px var(--dashboard-shadow);
            min-width: 0;
            padding: 1.05rem;
        }
        .about-card-primary {
            border-left: 4px solid var(--dashboard-primary);
        }
        .about-card-wide {
            margin-top: 1.05rem;
        }
        .about-kicker {
            color: var(--dashboard-primary);
            font-size: 0.78rem;
            font-weight: 850;
            letter-spacing: 0;
            margin-bottom: 0.55rem;
            text-transform: uppercase;
        }
        .about-title {
            color: var(--dashboard-text);
            font-size: clamp(1.35rem, 2.3vw, 2rem);
            font-weight: 900;
            line-height: 1.14;
            margin-bottom: 0.95rem;
        }
        .about-list {
            display: grid;
            gap: 0.55rem;
        }
        .about-row {
            background: color-mix(in srgb, var(--dashboard-primary) 4%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--dashboard-primary) 9%, var(--dashboard-border-muted));
            border-radius: 10px;
            display: grid;
            gap: 0.8rem;
            grid-template-columns: minmax(104px, 0.36fr) minmax(0, 1fr);
            padding: 0.62rem 0.7rem;
        }
        .about-row-label {
            color: var(--dashboard-muted);
            font-size: 0.78rem;
            font-weight: 800;
            line-height: 1.25;
        }
        .about-row-value {
            color: var(--dashboard-text);
            font-size: 0.92rem;
            font-weight: 760;
            line-height: 1.28;
        }
        .about-flow {
            display: grid;
            gap: 0.72rem;
            grid-template-columns: repeat(5, minmax(0, 1fr));
        }
        .about-step {
            background: color-mix(in srgb, var(--dashboard-primary) 5%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--dashboard-primary) 11%, var(--dashboard-border-muted));
            border-radius: 12px;
            min-width: 0;
            padding: 0.82rem 0.78rem;
        }
        .about-step span {
            align-items: center;
            background: var(--dashboard-primary);
            border-radius: 999px;
            color: #ffffff;
            display: inline-flex;
            font-size: 0.75rem;
            font-weight: 850;
            height: 1.45rem;
            justify-content: center;
            margin-bottom: 0.55rem;
            width: 1.45rem;
        }
        .about-step strong,
        .about-step small {
            display: block;
            line-height: 1.25;
        }
        .about-step strong {
            color: var(--dashboard-text);
            font-size: 0.9rem;
            font-weight: 850;
        }
        .about-step small {
            color: var(--dashboard-muted);
            font-size: 0.78rem;
            font-weight: 650;
            margin-top: 0.22rem;
        }
        .about-scope {
            color: var(--dashboard-muted);
            font-size: 0.94rem;
            font-weight: 650;
            line-height: 1.52;
            margin: 0.85rem 0 0.2rem;
        }
        .simulation-summary {
            display: grid;
            gap: 0.9rem;
            margin: 0.35rem 0 1.05rem;
        }
        .simulation-timeline {
            display: grid;
            gap: 0.8rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }
        .simulation-tile,
        .simulation-panel {
            background:
                linear-gradient(
                    135deg,
                    color-mix(in srgb, var(--dashboard-primary) 6%, var(--dashboard-card-bg)) 0%,
                    var(--dashboard-card-bg) 72%
                );
            border: 1px solid var(--dashboard-border-muted);
            border-radius: 12px;
            box-shadow: 0 10px 24px var(--dashboard-shadow);
            min-width: 0;
        }
        .simulation-tile {
            padding: 0.9rem 1rem;
        }
        .simulation-label {
            color: var(--dashboard-muted);
            font-size: 0.78rem;
            font-weight: 780;
            line-height: 1.25;
            margin-bottom: 0.28rem;
        }
        .simulation-value {
            color: var(--dashboard-text);
            font-size: 1.05rem;
            font-weight: 850;
            line-height: 1.18;
            overflow-wrap: anywhere;
        }
        .simulation-caption {
            color: var(--dashboard-muted);
            font-size: 0.78rem;
            font-weight: 620;
            line-height: 1.35;
            margin-top: 0.24rem;
        }
        .simulation-comparison {
            display: grid;
            gap: 0.9rem;
            grid-template-columns: 0.82fr 1fr 1fr;
        }
        .simulation-panel {
            border-top: 4px solid var(--sim-accent, var(--dashboard-primary));
            padding: 1rem;
            position: relative;
            transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
        }
        .simulation-panel:hover {
            border-color: color-mix(in srgb, var(--sim-accent, var(--dashboard-primary)) 36%, var(--dashboard-border-muted));
            box-shadow: 0 14px 30px var(--dashboard-shadow);
            transform: translateY(-1px);
        }
        .simulation-panel-title {
            align-items: center;
            color: var(--dashboard-text);
            display: flex;
            font-size: 1rem;
            font-weight: 860;
            gap: 0.45rem;
            justify-content: space-between;
            line-height: 1.2;
            margin-bottom: 0.75rem;
        }
        .simulation-pill {
            background: color-mix(in srgb, var(--sim-accent, var(--dashboard-primary)) 12%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--sim-accent, var(--dashboard-primary)) 26%, transparent);
            border-radius: 999px;
            color: var(--sim-accent, var(--dashboard-primary));
            font-size: 0.7rem;
            font-weight: 820;
            padding: 0.16rem 0.5rem;
            white-space: nowrap;
        }
        .simulation-panel-main {
            color: var(--dashboard-text);
            font-size: clamp(1.5rem, 2.7vw, 2.2rem);
            font-weight: 900;
            line-height: 1;
            margin-bottom: 0.85rem;
            overflow-wrap: anywhere;
        }
        .simulation-mini-grid {
            display: grid;
            gap: 0.55rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .simulation-mini {
            background: color-mix(in srgb, var(--sim-accent, var(--dashboard-primary)) 5%, var(--dashboard-card-bg));
            border: 1px solid color-mix(in srgb, var(--sim-accent, var(--dashboard-primary)) 12%, var(--dashboard-border-muted));
            border-radius: 10px;
            min-width: 0;
            padding: 0.62rem 0.66rem;
        }
        .simulation-mini .simulation-value {
            font-size: 1rem;
        }
        .simulation-accent-blue { --sim-accent: var(--dashboard-primary); }
        .simulation-accent-cyan { --sim-accent: var(--dashboard-cyan); }
        .simulation-accent-purple { --sim-accent: #6d5bd0; }
        @media (max-width: 980px) {
            .about-grid,
            .about-flow {
                grid-template-columns: 1fr;
            }
            .simulation-timeline,
            .simulation-comparison {
                grid-template-columns: 1fr;
            }
        }
        @media (max-width: 680px) {
            .about-row {
                grid-template-columns: 1fr;
            }
        }
        .stAlert {
            border-radius: 8px;
        }
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] p,
        label,
        [data-testid="stCaptionContainer"] {
            color: var(--dashboard-text);
        }
        div[data-testid="stHorizontalBlock"] > div:has(.thesis-card) {
            min-width: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, caption: str | None = None) -> None:
    caption_html = f"<p class='dashboard-page-caption'>{escape(caption)}</p>" if caption else ""
    st.markdown(
        f"""
        <div class="dashboard-page-header">
            <h1 class="dashboard-page-title">{escape(title)}</h1>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_title(title: str) -> None:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-logo" aria-hidden="true">
                <svg viewBox="0 0 64 64" role="img">
                    <path d="M17 46V18h18.2c6.2 0 10.4 3.2 10.4 8.2 0 3.1-1.6 5.5-4.4 6.8 3.5 1.2 5.6 3.9 5.6 7.6 0 5.3-4.5 8.9-11.2 8.9H17Zm11.2-17h5.1c2 0 3.2-1 3.2-2.7 0-1.7-1.2-2.6-3.2-2.6h-5.1V29Zm0 12.7h6c2.1 0 3.4-1.1 3.4-2.9s-1.3-2.9-3.4-2.9h-6v5.8Z" fill="#ffffff"/>
                    <path d="M13.5 49.5h37" stroke="#ffffff" stroke-opacity="0.82" stroke-width="4" stroke-linecap="round"/>
                    <path d="M49.5 15.5v15l-7.5-7.5 7.5-7.5Z" fill="#b9f7e5"/>
                </svg>
            </div>
            <div class="sidebar-brand-copy">
                <div class="sidebar-brand-name">{escape(title)}</div>
                <div class="sidebar-brand-tagline">Bitcoin Risk Analytics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def live_price_card(
    price: Any,
    change_percent: Any,
    high_24h: Any = None,
    low_24h: Any = None,
    volume_24h: Any = None,
    quote_volume_24h: Any = None,
    updated_at: str | None = None,
) -> None:
    dark_mode = bool(st.session_state.get("dark_theme_enabled", False))
    theme = {
        "primary": "#7aa2ff" if dark_mode else "#2f5fda",
        "card": "#121c2f" if dark_mode else "#ffffff",
        "text": "#e7edf7" if dark_mode else "#101828",
        "muted": "#9aa8bd" if dark_mode else "#667085",
        "border": "rgba(122, 162, 255, 0.30)" if dark_mode else "rgba(47, 95, 218, 0.20)",
        "borderMuted": "rgba(154, 168, 189, 0.22)" if dark_mode else "rgba(152, 162, 179, 0.36)",
        "shadow": "rgba(0, 0, 0, 0.35)" if dark_mode else "rgba(16, 24, 40, 0.07)",
        "success": "#4fd1a5" if dark_mode else "#168a69",
        "danger": "#fb7185" if dark_mode else "#c24150",
        "warning": "#f2b44b" if dark_mode else "#b86b0b",
    }
    initial_change = _to_float(change_percent)
    initial = {
        "price": _to_float(price),
        "changePercent": None if initial_change is None else initial_change * 100,
        "high": _to_float(high_24h),
        "low": _to_float(low_24h),
        "quoteVolume": _to_float(quote_volume_24h),
        "volume": _to_float(volume_24h),
        "updatedAtText": updated_at,
    }

    html = """
    <div id="live-card" class="card">
        <div class="main">
            <div class="asset">
                <div class="logo">B</div>
                <div class="name">Bitcoin <span>BTC</span></div>
                <div class="pill">#1</div>
                <div id="status" class="status connecting"><i></i><b>Connecting</b></div>
            </div>
            <div class="price-row">
                <div id="price" class="price">N/A</div>
                <div id="change" class="change">N/A</div>
            </div>
        </div>
        <div class="meta-grid">
            <div class="meta"><span>24h High</span><strong id="high">N/A</strong></div>
            <div class="meta"><span>24h Low</span><strong id="low">N/A</strong></div>
            <div class="meta"><span>24h Volume</span><strong id="volume">N/A</strong></div>
            <div class="meta"><span>Updated</span><strong id="updated">N/A</strong></div>
        </div>
    </div>

    <style>
        :root {
            --primary: __PRIMARY__;
            --card: __CARD__;
            --text: __TEXT__;
            --muted: __MUTED__;
            --border: __BORDER__;
            --border-muted: __BORDER_MUTED__;
            --shadow: __SHADOW__;
            --success: __SUCCESS__;
            --danger: __DANGER__;
            --warning: __WARNING__;
        }
        * { box-sizing: border-box; letter-spacing: 0; }
        body {
            margin: 0;
            overflow: hidden;
            font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;
            background: transparent;
            color: var(--text);
        }
        .card {
            background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 8%, var(--card)) 0%, var(--card) 60%);
            border: 1px solid var(--border);
            border-radius: 14px;
            box-shadow: 0 16px 36px var(--shadow);
            display: grid;
            gap: 1rem;
            grid-template-columns: minmax(0, 1fr) minmax(280px, 0.38fr);
            margin: 0;
            overflow: hidden;
            padding: 1.15rem 1.25rem;
            position: relative;
            width: 100%;
            min-height: 220px;
        }
        .card::before {
            background: var(--primary);
            bottom: 0;
            content: "";
            left: 0;
            position: absolute;
            top: 0;
            width: 4px;
        }
        .asset {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.72rem;
            margin-bottom: 1.05rem;
        }
        .logo {
            align-items: center;
            background: #f7931a;
            border-radius: 999px;
            color: #fff;
            display: inline-flex;
            font-size: 1rem;
            font-weight: 850;
            height: 44px;
            justify-content: center;
            width: 44px;
        }
        .name {
            color: var(--text);
            font-size: clamp(1.45rem, 2.1vw, 2.2rem);
            font-weight: 840;
            line-height: 1.05;
        }
        .name span {
            color: var(--muted);
            font-size: 1.05rem;
            font-weight: 720;
        }
        .pill,
        .status {
            align-items: center;
            background: color-mix(in srgb, var(--primary) 9%, var(--card));
            border: 1px solid color-mix(in srgb, var(--primary) 16%, transparent);
            border-radius: 999px;
            color: var(--text);
            display: inline-flex;
            font-size: 0.8rem;
            font-weight: 780;
            min-height: 30px;
            padding: 0.2rem 0.62rem;
        }
        .status {
            gap: 0.44rem;
        }
        .status i {
            background: var(--warning);
            border-radius: 999px;
            display: inline-block;
            height: 7px;
            width: 7px;
        }
        .status.live {
            background: color-mix(in srgb, var(--success) 10%, var(--card));
            border-color: color-mix(in srgb, var(--success) 22%, transparent);
        }
        .status.live i {
            background: var(--success);
        }
        .status.offline {
            background: color-mix(in srgb, var(--danger) 10%, var(--card));
            border-color: color-mix(in srgb, var(--danger) 22%, transparent);
        }
        .status.offline i {
            background: var(--danger);
        }
        .price-row {
            align-items: baseline;
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem 1rem;
        }
        .price {
            color: var(--text);
            font-size: clamp(2.8rem, 5.4vw, 5rem);
            font-weight: 850;
            line-height: 0.96;
            transition: opacity 120ms ease, transform 120ms ease;
        }
        .price.flash {
            opacity: 0.68;
            transform: translateY(-1px);
        }
        .change {
            border-radius: 999px;
            font-size: clamp(1rem, 1.5vw, 1.35rem);
            font-weight: 800;
            padding: 0.26rem 0.72rem;
        }
        .change.up {
            background: color-mix(in srgb, var(--success) 12%, var(--card));
            color: var(--success);
        }
        .change.down {
            background: color-mix(in srgb, var(--danger) 12%, var(--card));
            color: var(--danger);
        }
        .meta-grid {
            align-self: stretch;
            display: grid;
            gap: 0.68rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .meta {
            background: color-mix(in srgb, var(--primary) 5%, var(--card));
            border: 1px solid color-mix(in srgb, var(--primary) 10%, var(--border-muted));
            border-radius: 12px;
            min-width: 0;
            padding: 0.72rem 0.78rem;
        }
        .meta span {
            color: var(--muted);
            display: block;
            font-size: 0.72rem;
            font-weight: 760;
            margin-bottom: 0.24rem;
        }
        .meta strong {
            color: var(--text);
            display: block;
            font-size: 0.95rem;
            font-weight: 820;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }
        @media (max-width: 760px) {
            .card { grid-template-columns: 1fr; }
            .meta-grid { grid-template-columns: 1fr 1fr; }
        }
    </style>

    <script>
        const initial = __INITIAL__;
        const statusEl = document.getElementById("status");
        const statusText = statusEl.querySelector("b");
        const els = {
            price: document.getElementById("price"),
            change: document.getElementById("change"),
            high: document.getElementById("high"),
            low: document.getElementById("low"),
            volume: document.getElementById("volume"),
            updated: document.getElementById("updated"),
        };
        let ws = null;
        let reconnectTimer = null;

        function numberOrNull(value) {
            const num = Number(value);
            return Number.isFinite(num) ? num : null;
        }

        function money(value) {
            const num = numberOrNull(value);
            if (num === null) return "N/A";
            return "$" + num.toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            });
        }

        function compactMoney(value) {
            const num = numberOrNull(value);
            if (num === null) return "N/A";
            const abs = Math.abs(num);
            if (abs >= 1e9) return "$" + (num / 1e9).toFixed(2) + "B";
            if (abs >= 1e6) return "$" + (num / 1e6).toFixed(2) + "M";
            if (abs >= 1e3) return "$" + (num / 1e3).toFixed(2) + "K";
            return money(num);
        }

        function pct(value) {
            const num = numberOrNull(value);
            if (num === null) return "N/A";
            return (num >= 0 ? "+" : "") + num.toFixed(2) + "% (24h)";
        }

        function timeText(value) {
            if (!value) return "N/A";
            if (typeof value === "string" && value.includes("UTC")) return value;
            const d = new Date(Number(value));
            if (Number.isNaN(d.getTime())) return "N/A";
            return d.toISOString().slice(0, 16).replace("T", " ") + " UTC";
        }

        function setStatus(label, className) {
            statusText.textContent = label;
            statusEl.className = "status " + className;
        }

        function render(data, live) {
            if (data.price !== null && data.price !== undefined) {
                els.price.textContent = money(data.price);
                els.price.classList.add("flash");
                setTimeout(() => els.price.classList.remove("flash"), 120);
            }
            if (data.changePercent !== null && data.changePercent !== undefined) {
                els.change.textContent = pct(data.changePercent);
                els.change.className = "change " + (Number(data.changePercent) >= 0 ? "up" : "down");
            }
            els.high.textContent = money(data.high);
            els.low.textContent = money(data.low);
            els.volume.textContent = compactMoney(data.quoteVolume ?? data.volume);
            els.updated.textContent = data.updatedAtText || timeText(data.updatedAt);
            if (live) setStatus("Live", "live");
        }

        function tickerToData(payload) {
            return {
                price: numberOrNull(payload.c ?? payload.lastPrice),
                changePercent: numberOrNull(payload.P ?? payload.priceChangePercent),
                high: numberOrNull(payload.h ?? payload.highPrice),
                low: numberOrNull(payload.l ?? payload.lowPrice),
                volume: numberOrNull(payload.v ?? payload.volume),
                quoteVolume: numberOrNull(payload.q ?? payload.quoteVolume),
                updatedAt: payload.E ?? payload.closeTime,
            };
        }

        async function fetchRestSnapshot() {
            const bases = [
                "https://api.binance.com",
                "https://api1.binance.com",
                "https://api2.binance.com",
                "https://data-api.binance.vision",
            ];
            for (const base of bases) {
                try {
                    const response = await fetch(base + "/api/v3/ticker/24hr?symbol=BTCUSDT", { cache: "no-store" });
                    if (!response.ok) continue;
                    const payload = await response.json();
                    render(tickerToData(payload), false);
                    return true;
                } catch (error) {}
            }
            return false;
        }

        function connectStream() {
            clearTimeout(reconnectTimer);
            setStatus("Connecting", "connecting");
            try {
                ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker");
            } catch (error) {
                scheduleReconnect();
                return;
            }
            ws.onopen = () => setStatus("Live", "live");
            ws.onmessage = (event) => {
                try {
                    render(tickerToData(JSON.parse(event.data)), true);
                } catch (error) {}
            };
            ws.onerror = () => {
                setStatus("Reconnecting", "offline");
                try { ws.close(); } catch (error) {}
            };
            ws.onclose = () => scheduleReconnect();
        }

        function scheduleReconnect() {
            setStatus("Reconnecting", "offline");
            fetchRestSnapshot();
            reconnectTimer = setTimeout(connectStream, 3000);
        }

        render(initial, false);
        fetchRestSnapshot();
        connectStream();
        setInterval(fetchRestSnapshot, 30000);
    </script>
    """

    replacements = {
        "__PRIMARY__": theme["primary"],
        "__CARD__": theme["card"],
        "__TEXT__": theme["text"],
        "__MUTED__": theme["muted"],
        "__BORDER__": theme["border"],
        "__BORDER_MUTED__": theme["borderMuted"],
        "__SHADOW__": theme["shadow"],
        "__SUCCESS__": theme["success"],
        "__DANGER__": theme["danger"],
        "__WARNING__": theme["warning"],
        "__INITIAL__": json.dumps(initial),
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    st.iframe(html, height=240)


def realtime_risk_charts(
    btc_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    model: str,
    confidence: str,
) -> None:
    dark_mode = bool(st.session_state.get("dark_theme_enabled", False))
    theme = {
        "primary": "#7aa2ff" if dark_mode else "#2f5fda",
        "card": "#121c2f" if dark_mode else "#ffffff",
        "text": "#e7edf7" if dark_mode else "#101828",
        "muted": "#9aa8bd" if dark_mode else "#667085",
        "border": "rgba(122, 162, 255, 0.30)" if dark_mode else "rgba(47, 95, 218, 0.20)",
        "grid": "rgba(168, 180, 199, 0.22)" if dark_mode else "rgba(148, 163, 184, 0.28)",
        "plot": "rgba(18, 28, 47, 0.00)" if dark_mode else "rgba(255, 255, 255, 0.00)",
        "paper": "rgba(18, 28, 47, 0.00)" if dark_mode else "rgba(255, 255, 255, 0.00)",
        "shadow": "rgba(0, 0, 0, 0.35)" if dark_mode else "rgba(16, 24, 40, 0.07)",
        "loss": "#8290a3" if dark_mode else "#5b677a",
        "return": "#8fa0b8" if dark_mode else "#5b677a",
        "realized": "#94a3b8" if dark_mode else "#98a2b3",
        "ms": "#38bdf8" if dark_mode else "#0f7f8f",
        "sv": "#a78bfa" if dark_mode else "#6d5bd0",
        "cvar": "#f2b44b" if dark_mode else "#b86b0b",
        "breach": "#fb7185" if dark_mode else "#b4234a",
    }
    payload = {
        "btc": _btc_chart_records(btc_df),
        "risk": _risk_chart_records(risk_df, model, confidence),
        "models": _chart_models(model),
        "confidence": confidence,
        "theme": theme,
    }
    payload_json = json.dumps(payload, allow_nan=False)

    html = """
    <div class="chart-grid">
        <section class="chart-card chart-card-main">
            <div id="risk-chart" class="chart chart-main"></div>
        </section>
        <section class="chart-card">
            <div id="return-chart" class="chart"></div>
        </section>
        <section class="chart-card">
            <div id="vol-chart" class="chart"></div>
        </section>
        <section class="chart-card chart-card-main">
            <div class="table-title">Daily Risk Summary</div>
            <div class="table-scroll">
                <table>
                    <thead id="risk-table-head"></thead>
                    <tbody id="risk-table-body"></tbody>
                </table>
            </div>
        </section>
    </div>

    <style>
        :root {
            --primary: __PRIMARY__;
            --card: __CARD__;
            --text: __TEXT__;
            --muted: __MUTED__;
            --border: __BORDER__;
            --shadow: __SHADOW__;
        }
        * { box-sizing: border-box; letter-spacing: 0; }
        body {
            background: transparent;
            color: var(--text);
            font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;
            margin: 0;
            overflow: hidden;
        }
        .chart-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            width: 100%;
        }
        .chart-card {
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--primary) 7%, var(--card)) 0%, var(--card) 70%);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 12px 28px var(--shadow);
            min-width: 0;
            overflow: hidden;
            padding: 0.7rem 0.7rem 0.25rem;
        }
        .chart-card-main {
            grid-column: 1 / -1;
        }
        .chart {
            height: 430px;
            width: 100%;
        }
        .chart-main {
            height: 560px;
        }
        .table-title {
            color: var(--text);
            font-size: 1.35rem;
            font-weight: 840;
            line-height: 1.2;
            margin: 0.45rem 0 0.8rem;
        }
        .table-scroll {
            border: 1px solid color-mix(in srgb, var(--primary) 10%, var(--border));
            border-radius: 10px;
            max-height: 390px;
            overflow: auto;
        }
        table {
            border-collapse: collapse;
            min-width: 980px;
            width: 100%;
        }
        th,
        td {
            border-bottom: 1px solid color-mix(in srgb, var(--primary) 8%, var(--border));
            color: var(--text);
            font-size: 0.88rem;
            padding: 0.72rem 0.75rem;
            text-align: right;
            white-space: nowrap;
        }
        th {
            background: color-mix(in srgb, var(--primary) 8%, var(--card));
            color: var(--muted);
            font-weight: 820;
            position: sticky;
            top: 0;
            z-index: 1;
        }
        th:first-child,
        td:first-child {
            text-align: left;
        }
        tr.live-row td {
            background: color-mix(in srgb, var(--primary) 7%, transparent);
            font-weight: 800;
        }
        .breach-pill {
            border-radius: 999px;
            display: inline-flex;
            font-size: 0.78rem;
            font-weight: 850;
            justify-content: center;
            min-width: 72px;
            padding: 0.18rem 0.52rem;
        }
        .breach-yes {
            background: color-mix(in srgb, __BREACH__ 14%, transparent);
            color: __BREACH__;
        }
        .breach-no {
            background: color-mix(in srgb, var(--primary) 11%, transparent);
            color: var(--primary);
        }
        @media (max-width: 900px) {
            .chart-grid { grid-template-columns: 1fr; }
        }
    </style>

    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <script>
        const payload = __PAYLOAD__;
        const theme = payload.theme;
        const config = { displayModeBar: false, responsive: true };
        const restBases = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://data-api.binance.vision",
        ];
        let btcRows = payload.btc.map(normalizeBtcRow).filter(row => row.t !== null);
        const riskRows = payload.risk.map(normalizeRiskRow).filter(row => row.t !== null);
        let ws = null;
        let reconnectTimer = null;
        let lastRenderMs = 0;

        function num(value) {
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : null;
        }

        function normalizeBtcRow(row) {
            return {
                t: toMs(row.t),
                close: num(row.close),
                ret: num(row.ret),
                loss: num(row.loss),
                vol: num(row.vol),
            };
        }

        function normalizeRiskRow(row) {
            const normalized = { t: toMs(row.t), actual_loss: num(row.actual_loss) };
            for (const key of Object.keys(row)) {
                if (key !== "t" && key !== "actual_loss") normalized[key] = num(row[key]);
            }
            return normalized;
        }

        function toMs(value) {
            if (!value) return null;
            const parsed = new Date(value).getTime();
            return Number.isFinite(parsed) ? parsed : null;
        }

        function iso(ms) {
            return new Date(ms).toISOString();
        }

        function dayKey(ms) {
            return new Date(ms).toISOString().slice(0, 10);
        }

        function utcDayStart(ms) {
            const date = new Date(ms);
            return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        }

        function mergeBtcRows(incoming) {
            const byDay = new Map();
            for (const row of btcRows) byDay.set(dayKey(row.t), row);
            for (const row of incoming) {
                if (row.t === null) continue;
                const key = dayKey(row.t);
                byDay.set(key, { ...(byDay.get(key) || {}), ...row });
            }
            btcRows = recomputeDerived([...byDay.values()].sort((a, b) => a.t - b.t));
        }

        function recomputeDerived(rows) {
            const returns = [];
            let prevClose = null;
            for (const row of rows) {
                if (row.close !== null && prevClose !== null && row.close > 0 && prevClose > 0) {
                    row.ret = Math.log(row.close / prevClose);
                }
                if (row.ret !== null) row.loss = -row.ret;
                returns.push(row.ret);
                const windowValues = returns.slice(-30).filter(value => value !== null);
                if (windowValues.length >= 2) row.vol = std(windowValues);
                prevClose = row.close !== null ? row.close : prevClose;
            }
            return rows;
        }

        function std(values) {
            const mean = values.reduce((total, value) => total + value, 0) / values.length;
            const variance = values.reduce((total, value) => total + Math.pow(value - mean, 2), 0) / (values.length - 1);
            return Math.sqrt(variance);
        }

        function riskStartMs() {
            if (riskRows.length) return riskRows[0].t;
            const last = btcRows[btcRows.length - 1]?.t;
            return last ? last - 900 * 24 * 60 * 60 * 1000 : null;
        }

        function lastBtcMs() {
            return btcRows.length ? btcRows[btcRows.length - 1].t : null;
        }

        function baseLayout(title, yTitle, height) {
            return {
                title: { text: title, font: { color: theme.text, size: 18 } },
                height,
                margin: { l: 58, r: 24, t: 62, b: 58 },
                paper_bgcolor: theme.paper,
                plot_bgcolor: theme.plot,
                font: { color: theme.text, family: "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" },
                hovermode: "x unified",
                hoverlabel: {
                    bgcolor: theme.card,
                    bordercolor: theme.border,
                    font: { color: theme.text },
                },
                legend: {
                    orientation: "h",
                    x: 0,
                    y: -0.18,
                    font: { color: theme.text, size: 12 },
                },
                xaxis: {
                    type: "date",
                    gridcolor: theme.grid,
                    zerolinecolor: theme.grid,
                    tickfont: { color: theme.text },
                },
                yaxis: {
                    title: { text: yTitle, font: { color: theme.text } },
                    tickformat: ".1%",
                    gridcolor: theme.grid,
                    zerolinecolor: theme.grid,
                    tickfont: { color: theme.text },
                },
            };
        }

        function riskThreshold(model, field) {
            const column = model.key + "_" + field;
            const rows = riskRows
                .map(row => ({ t: row.t, value: row[column] }))
                .filter(row => row.value !== null);
            return {
                rows,
                last: rows.length ? rows[rows.length - 1] : null,
            };
        }

        function thresholdForDate(model, field, ms) {
            const column = model.key + "_" + field;
            let last = null;
            for (const row of riskRows) {
                const value = row[column];
                if (value === null) continue;
                if (dayKey(row.t) === dayKey(ms)) return value;
                if (row.t <= ms) last = { t: row.t, value };
            }
            return last && ms > last.t ? last.value : null;
        }

        function modelColor(model) {
            return model.key === "SV" ? theme.sv : theme.ms;
        }

        function fmtDate(ms) {
            return new Date(ms).toISOString().slice(0, 10);
        }

        function fmtPct(value) {
            const parsed = num(value);
            return parsed === null ? "N/A" : (parsed * 100).toFixed(2) + "%";
        }

        function latestModelValue(model, field) {
            const series = riskThreshold(model, field);
            return series.last ? series.last.value : null;
        }

        function riskRowsForTable() {
            const rowsByDay = new Map();
            for (const row of riskRows) {
                const tableRow = {
                    t: row.t,
                    actual_return: row.actual_loss === null ? null : -row.actual_loss,
                    actual_loss: row.actual_loss,
                    live: false,
                };
                for (const model of payload.models) {
                    tableRow[model.key + "_sigma"] = row[model.key + "_sigma"];
                    tableRow[model.key + "_VaR"] = row[model.key + "_VaR"];
                    tableRow[model.key + "_CVaR"] = row[model.key + "_CVaR"];
                    tableRow[model.key + "_breach"] =
                        row.actual_loss !== null && row[model.key + "_VaR"] !== null && row.actual_loss > row[model.key + "_VaR"];
                }
                if (row.MS_GARCH_p_high !== undefined) tableRow.MS_GARCH_p_high = row.MS_GARCH_p_high;
                rowsByDay.set(dayKey(row.t), tableRow);
            }

            const latest = btcRows[btcRows.length - 1];
            if (latest && latest.ret !== null) {
                const liveRow = rowsByDay.get(dayKey(latest.t)) || { t: latest.t };
                liveRow.t = latest.t;
                liveRow.actual_return = latest.ret;
                liveRow.actual_loss = latest.loss;
                liveRow.live = true;
                for (const model of payload.models) {
                    liveRow[model.key + "_sigma"] = latestModelValue(model, "sigma");
                    liveRow[model.key + "_VaR"] = latestModelValue(model, "VaR");
                    liveRow[model.key + "_CVaR"] = latestModelValue(model, "CVaR");
                    liveRow[model.key + "_breach"] =
                        latest.loss !== null && liveRow[model.key + "_VaR"] !== null && latest.loss > liveRow[model.key + "_VaR"];
                }
                rowsByDay.set(dayKey(latest.t), liveRow);
            }
            return [...rowsByDay.values()].sort((a, b) => b.t - a.t).slice(0, 30);
        }

        function renderRiskTable() {
            const head = document.getElementById("risk-table-head");
            const body = document.getElementById("risk-table-body");
            const modelHeaders = payload.models.flatMap(model => [
                model.label + " Sigma",
                model.label + " VaR " + payload.confidence,
                model.label + " CVaR " + payload.confidence,
                model.label + " Breach",
            ]);
            const headers = ["Open Time", "Actual Return", "Actual Loss", ...modelHeaders];
            head.innerHTML = "<tr>" + headers.map(label => "<th>" + label + "</th>").join("") + "</tr>";
            body.innerHTML = riskRowsForTable().map(row => {
                const cells = [
                    fmtDate(row.t) + (row.live ? " · Live" : ""),
                    fmtPct(row.actual_return),
                    fmtPct(row.actual_loss),
                ];
                for (const model of payload.models) {
                    const breached = row[model.key + "_breach"];
                    const breachCell = breached ? "<span class='breach-pill breach-yes'>Breach</span>" : "";
                    cells.push(
                        fmtPct(row[model.key + "_sigma"]),
                        fmtPct(row[model.key + "_VaR"]),
                        fmtPct(row[model.key + "_CVaR"]),
                        breachCell,
                    );
                }
                return "<tr class='" + (row.live ? "live-row" : "") + "'>" + cells.map(value => "<td>" + value + "</td>").join("") + "</tr>";
            }).join("");
        }

        function renderRiskChart() {
            const start = riskStartMs();
            const lossRows = btcRows.filter(row => row.loss !== null && (start === null || row.t >= start));
            const traces = [{
                x: lossRows.map(row => iso(row.t)),
                y: lossRows.map(row => row.loss),
                mode: "lines",
                name: "Realized Loss",
                line: { color: theme.loss, width: 1.45 },
                hovertemplate: "%{x|%Y-%m-%d}<br>Loss: %{y:.4%}<extra></extra>",
            }];
            const latestMs = lastBtcMs();

            for (const model of payload.models) {
                const varSeries = riskThreshold(model, "VaR");
                traces.push({
                    x: varSeries.rows.map(row => iso(row.t)),
                    y: varSeries.rows.map(row => row.value),
                    mode: "lines",
                    name: model.label + " VaR " + payload.confidence + "%",
                    line: { color: modelColor(model), width: 2 },
                    hovertemplate: "%{x|%Y-%m-%d}<br>VaR: %{y:.4%}<extra></extra>",
                });
                if (latestMs && varSeries.last && latestMs > varSeries.last.t) {
                    traces.push({
                        x: [iso(varSeries.last.t), iso(latestMs)],
                        y: [varSeries.last.value, varSeries.last.value],
                        mode: "lines",
                        name: model.label + " last modeled VaR",
                        line: { color: modelColor(model), width: 1.6, dash: "dot" },
                        hovertemplate: "%{x|%Y-%m-%d}<br>Last VaR: %{y:.4%}<extra></extra>",
                    });
                }

                if (payload.models.length === 1) {
                    const cvarSeries = riskThreshold(model, "CVaR");
                    if (cvarSeries.rows.length) {
                        traces.push({
                            x: cvarSeries.rows.map(row => iso(row.t)),
                            y: cvarSeries.rows.map(row => row.value),
                            mode: "lines",
                            name: model.label + " CVaR " + payload.confidence + "%",
                            line: { color: theme.cvar, width: 1.8, dash: "dot" },
                            hovertemplate: "%{x|%Y-%m-%d}<br>CVaR: %{y:.4%}<extra></extra>",
                        });
                    }
                }

                const breachRows = lossRows.filter(row => {
                    const threshold = thresholdForDate(model, "VaR", row.t);
                    return threshold !== null && row.loss > threshold;
                });
                if (breachRows.length) {
                    traces.push({
                        x: breachRows.map(row => iso(row.t)),
                        y: breachRows.map(row => row.loss),
                        mode: "markers",
                        name: model.label + " Breach",
                        marker: { color: theme.breach, size: 7, symbol: "x" },
                        hovertemplate: "%{x|%Y-%m-%d}<br>Breach Loss: %{y:.4%}<extra></extra>",
                    });
                }
            }

            Plotly.react(
                "risk-chart",
                traces,
                baseLayout("Realized Loss vs VaR " + payload.confidence + "%", "Loss / Risk Threshold", 560),
                config,
            );
        }

        function renderReturnChart() {
            const rows = btcRows.filter(row => row.ret !== null);
            const traces = [{
                x: rows.map(row => iso(row.t)),
                y: rows.map(row => row.ret),
                mode: "lines",
                name: "Log Return",
                line: { color: theme.return, width: 1.35 },
                hovertemplate: "%{x|%Y-%m-%d}<br>Log Return: %{y:.4%}<extra></extra>",
            }];
            const layout = baseLayout("Daily Log Return", "Log Return", 430);
            layout.shapes = [{
                type: "line",
                xref: "paper",
                x0: 0,
                x1: 1,
                y0: 0,
                y1: 0,
                line: { color: theme.grid, width: 1 },
            }];
            Plotly.react("return-chart", traces, layout, config);
        }

        function renderVolChart() {
            const volRows = btcRows.filter(row => row.vol !== null);
            const traces = [{
                x: volRows.map(row => iso(row.t)),
                y: volRows.map(row => row.vol),
                mode: "lines",
                name: "30D Realized Volatility",
                line: { color: theme.realized, width: 1.5, dash: "dot" },
                hovertemplate: "%{x|%Y-%m-%d}<br>Realized Vol: %{y:.4%}<extra></extra>",
            }];
            const latestMs = lastBtcMs();
            for (const model of payload.models) {
                const sigmaSeries = riskThreshold(model, "sigma");
                traces.push({
                    x: sigmaSeries.rows.map(row => iso(row.t)),
                    y: sigmaSeries.rows.map(row => row.value),
                    mode: "lines",
                    name: model.label + " Sigma",
                    line: { color: modelColor(model), width: 2 },
                    hovertemplate: "%{x|%Y-%m-%d}<br>Sigma: %{y:.4%}<extra></extra>",
                });
                if (latestMs && sigmaSeries.last && latestMs > sigmaSeries.last.t) {
                    traces.push({
                        x: [iso(sigmaSeries.last.t), iso(latestMs)],
                        y: [sigmaSeries.last.value, sigmaSeries.last.value],
                        mode: "lines",
                        name: model.label + " last sigma",
                        line: { color: modelColor(model), width: 1.6, dash: "dot" },
                        hovertemplate: "%{x|%Y-%m-%d}<br>Last Sigma: %{y:.4%}<extra></extra>",
                    });
                }
            }
            Plotly.react("vol-chart", traces, baseLayout("Volatility Comparison", "Volatility / Sigma", 430), config);
        }

        function renderAll() {
            if (!window.Plotly) {
                setTimeout(renderAll, 120);
                return;
            }
            lastRenderMs = Date.now();
            renderRiskChart();
            renderReturnChart();
            renderVolChart();
            renderRiskTable();
        }

        function renderThrottled() {
            if (Date.now() - lastRenderMs > 900) {
                renderAll();
            }
        }

        async function fetchDailyCandles() {
            for (const base of restBases) {
                try {
                    const response = await fetch(base + "/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=120", { cache: "no-store" });
                    if (!response.ok) continue;
                    const payload = await response.json();
                    mergeBtcRows(payload.map(row => ({
                        t: Number(row[0]),
                        close: num(row[4]),
                    })));
                    renderAll();
                    return true;
                } catch (error) {}
            }
            return false;
        }

        function updateLivePrice(price, eventTime) {
            const livePrice = num(price);
            const liveTime = num(eventTime) || Date.now();
            if (livePrice === null) return;
            mergeBtcRows([{ t: utcDayStart(liveTime), close: livePrice }]);
            renderThrottled();
        }

        function connectStream() {
            clearTimeout(reconnectTimer);
            try {
                ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker");
            } catch (error) {
                scheduleReconnect();
                return;
            }
            ws.onmessage = event => {
                try {
                    const tick = JSON.parse(event.data);
                    updateLivePrice(tick.c, tick.E);
                } catch (error) {}
            };
            ws.onerror = () => {
                try { ws.close(); } catch (error) {}
            };
            ws.onclose = () => scheduleReconnect();
        }

        function scheduleReconnect() {
            fetchDailyCandles();
            reconnectTimer = setTimeout(connectStream, 3000);
        }

        window.addEventListener("resize", () => {
            for (const id of ["risk-chart", "return-chart", "vol-chart"]) {
                const element = document.getElementById(id);
                if (window.Plotly && element) Plotly.Plots.resize(element);
            }
        });

        btcRows = recomputeDerived(btcRows.sort((a, b) => a.t - b.t));
        renderAll();
        fetchDailyCandles();
        connectStream();
        setInterval(fetchDailyCandles, 60000);
    </script>
    """

    replacements = {
        "__PRIMARY__": theme["primary"],
        "__CARD__": theme["card"],
        "__TEXT__": theme["text"],
        "__MUTED__": theme["muted"],
        "__BORDER__": theme["border"],
        "__SHADOW__": theme["shadow"],
        "__BREACH__": theme["breach"],
        "__PAYLOAD__": payload_json,
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    st.iframe(html, height=1060)


def realtime_forecast_panel(forecast_df: pd.DataFrame, price_demo_df: pd.DataFrame, model: str) -> None:
    dark_mode = bool(st.session_state.get("dark_theme_enabled", False))
    theme = {
        "primary": "#7aa2ff" if dark_mode else "#2f5fda",
        "card": "#121c2f" if dark_mode else "#ffffff",
        "text": "#e7edf7" if dark_mode else "#101828",
        "muted": "#9aa8bd" if dark_mode else "#667085",
        "border": "rgba(122, 162, 255, 0.30)" if dark_mode else "rgba(47, 95, 218, 0.20)",
        "grid": "rgba(168, 180, 199, 0.22)" if dark_mode else "rgba(148, 163, 184, 0.28)",
        "shadow": "rgba(0, 0, 0, 0.35)" if dark_mode else "rgba(16, 24, 40, 0.07)",
        "success": "#4fd1a5" if dark_mode else "#168a69",
        "danger": "#fb7185" if dark_mode else "#c24150",
        "warning": "#f2b44b" if dark_mode else "#b86b0b",
        "actual": "#60a5fa" if dark_mode else "#2563eb",
        "live": "#f59e0b" if dark_mode else "#c56f00",
        "ms": "#22d3ee" if dark_mode else "#0f7f8f",
        "sv": "#c084fc" if dark_mode else "#6d5bd0",
    }
    payload = {
        "forecasts": _forecast_records(forecast_df, model),
        "priceDemo": _price_demo_records(price_demo_df),
        "models": _chart_models(model),
        "theme": theme,
    }
    payload_json = json.dumps(payload, allow_nan=False)

    html = """
    <div class="forecast-wrap">
        <div id="forecast-cards" class="cards"></div>
        <section class="panel">
            <div class="chart-head">
                <div>
                    <div class="chart-title">Current BTC Price vs Tomorrow Forecast</div>
                    <div class="chart-subtitle">Markers separate the current live BTC price from each model's next-day forecast.</div>
                </div>
                <div id="forecast-range-buttons" class="range-buttons"></div>
            </div>
            <div id="forecast-chart" class="chart"></div>
        </section>
        <section class="panel">
            <div class="table-title">Live Forecast Table</div>
            <div class="table-scroll">
                <table>
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Forecast Date</th>
                            <th>Current Price</th>
                            <th>Forecast Price</th>
                            <th>Model Return</th>
                            <th>Live Return</th>
                            <th>VaR 95</th>
                            <th>CVaR 95</th>
                            <th>VaR 99</th>
                            <th>CVaR 99</th>
                        </tr>
                    </thead>
                    <tbody id="forecast-table-body"></tbody>
                </table>
            </div>
        </section>
    </div>

    <style>
        :root {
            --primary: __PRIMARY__;
            --card: __CARD__;
            --text: __TEXT__;
            --muted: __MUTED__;
            --border: __BORDER__;
            --shadow: __SHADOW__;
            --success: __SUCCESS__;
            --danger: __DANGER__;
            --warning: __WARNING__;
        }
        * { box-sizing: border-box; letter-spacing: 0; }
        body {
            background: transparent;
            color: var(--text);
            font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;
            margin: 0;
            overflow: hidden;
        }
        .forecast-wrap {
            display: grid;
            gap: 1rem;
            width: 100%;
        }
        .cards {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
        }
        .card,
        .panel {
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--primary) 7%, var(--card)) 0%, var(--card) 70%);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 12px 28px var(--shadow);
            overflow: hidden;
        }
        .card {
            padding: 1rem 1.05rem;
        }
        .card-head {
            align-items: center;
            display: flex;
            gap: 0.6rem;
            justify-content: space-between;
            margin-bottom: 0.8rem;
        }
        .forecast-pill {
            background: color-mix(in srgb, var(--primary) 12%, var(--card));
            border: 1px solid color-mix(in srgb, var(--primary) 18%, var(--border));
            border-radius: 999px;
            color: var(--primary);
            font-size: 0.72rem;
            font-weight: 850;
            padding: 0.22rem 0.55rem;
            white-space: nowrap;
        }
        .model {
            color: var(--text);
            font-size: 1.12rem;
            font-weight: 850;
        }
        .forecast-price {
            color: var(--text);
            font-size: clamp(2rem, 4vw, 3.3rem);
            font-weight: 860;
            line-height: 1;
            margin-bottom: 0.28rem;
        }
        .forecast-caption {
            color: var(--muted);
            font-size: 0.8rem;
            font-weight: 720;
            margin-bottom: 0.85rem;
        }
        .mini-grid {
            display: grid;
            gap: 0.55rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .mini {
            background: color-mix(in srgb, var(--primary) 6%, var(--card));
            border: 1px solid color-mix(in srgb, var(--primary) 10%, var(--border));
            border-radius: 10px;
            padding: 0.66rem 0.7rem;
        }
        .mini span {
            color: var(--muted);
            display: block;
            font-size: 0.72rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        .mini strong {
            color: var(--text);
            display: block;
            font-size: 1rem;
            font-weight: 850;
        }
        .chart-head {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.85rem;
            justify-content: space-between;
            padding: 1rem 1rem 0;
        }
        .chart-title {
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 850;
            line-height: 1.2;
        }
        .chart-subtitle {
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 650;
            line-height: 1.35;
            margin-top: 0.18rem;
        }
        .range-buttons {
            background: color-mix(in srgb, var(--primary) 5%, var(--card));
            border: 1px solid var(--border);
            border-radius: 10px;
            display: grid;
            grid-auto-columns: minmax(54px, 1fr);
            grid-auto-flow: column;
            max-width: min(100%, 520px);
            overflow: hidden;
        }
        .range-btn {
            appearance: none;
            background: transparent;
            border: 0;
            border-right: 1px solid var(--border);
            color: var(--text);
            cursor: pointer;
            font: inherit;
            font-size: 0.84rem;
            font-weight: 760;
            min-height: 38px;
            padding: 0.42rem 0.68rem;
            transition: background-color 140ms ease, color 140ms ease;
        }
        .range-btn:last-child {
            border-right: 0;
        }
        .range-btn:hover {
            background: color-mix(in srgb, var(--primary) 11%, var(--card));
        }
        .range-btn.active {
            background: color-mix(in srgb, var(--primary) 22%, var(--card));
            box-shadow: inset 0 0 0 1px var(--primary);
            color: var(--primary);
        }
        .chart {
            height: 500px;
            width: 100%;
        }
        .table-title {
            color: var(--text);
            font-size: 1.25rem;
            font-weight: 840;
            line-height: 1.2;
            padding: 1rem 1rem 0.55rem;
        }
        .table-scroll {
            margin: 0 1rem 1rem;
            overflow: auto;
        }
        table {
            border-collapse: collapse;
            min-width: 980px;
            width: 100%;
        }
        th,
        td {
            border-bottom: 1px solid color-mix(in srgb, var(--primary) 8%, var(--border));
            color: var(--text);
            font-size: 0.88rem;
            padding: 0.7rem 0.75rem;
            text-align: right;
            white-space: nowrap;
        }
        th {
            background: color-mix(in srgb, var(--primary) 8%, var(--card));
            color: var(--muted);
            font-weight: 820;
        }
        th:first-child,
        td:first-child {
            text-align: left;
        }
    </style>

    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <script>
        const payload = __PAYLOAD__;
        const theme = payload.theme;
        const config = { displayModeBar: false, responsive: true };
        const restBases = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://data-api.binance.vision",
        ];
        let live = {
            price: firstNumber(payload.forecasts.map(row => row.lastClose)),
            updatedAt: null,
        };
        let selectedRange = "30D";
        let chartCandles = [];
        let ws = null;
        let reconnectTimer = null;

        function numberOrNull(value) {
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : null;
        }

        function firstNumber(values) {
            for (const value of values) {
                const parsed = numberOrNull(value);
                if (parsed !== null) return parsed;
            }
            return null;
        }

        function money(value) {
            const parsed = numberOrNull(value);
            return parsed === null ? "N/A" : "$" + parsed.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function pct(value) {
            const parsed = numberOrNull(value);
            return parsed === null ? "N/A" : (parsed * 100).toFixed(2) + "%";
        }

        function dateText(value) {
            if (!value) return "N/A";
            const parsed = new Date(value);
            return Number.isNaN(parsed.getTime()) ? "N/A" : parsed.toISOString().slice(0, 10);
        }

        function localDateString(offsetDays = 0) {
            const date = new Date();
            date.setDate(date.getDate() + offsetDays);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, "0");
            const day = String(date.getDate()).padStart(2, "0");
            return `${year}-${month}-${day}`;
        }

        function tomorrowDateString() {
            return localDateString(1);
        }

        function forecastTimestamp(row) {
            const current = new Date(currentTimestamp());
            current.setDate(current.getDate() + 1);
            return current.toISOString();
        }

        function currentTimestamp() {
            if (live.updatedAt) {
                const parsed = new Date(live.updatedAt);
                if (!Number.isNaN(parsed.getTime())) return parsed.toISOString();
            }
            return new Date().toISOString();
        }

        function forecastDateFor(row) {
            return tomorrowDateString();
        }

        function modelColor(modelKey) {
            return modelKey === "SV" ? theme.sv : theme.ms;
        }

        function modelForecastSymbol(modelKey) {
            return modelKey === "SV" ? "diamond" : "square";
        }

        function modelLineDash(modelKey) {
            return modelKey === "SV" ? "dash" : "dot";
        }

        function rangeOptions() {
            return [
                { label: "1D", days: 1, interval: "15m", limit: 96 },
                { label: "7D", days: 7, interval: "1h", limit: 168 },
                { label: "14D", days: 14, interval: "2h", limit: 168 },
                { label: "30D", days: 30, interval: "4h", limit: 180 },
                { label: "90D", days: 90, interval: "1d", limit: 90 },
                { label: "All", days: null, interval: null, limit: null },
            ];
        }

        function currentRange() {
            return rangeOptions().find(item => item.label === selectedRange) || rangeOptions()[3];
        }

        function latestObservedDate() {
            const dates = [];
            if (live.updatedAt) dates.push(new Date(live.updatedAt));
            if (chartCandles.length > 0) dates.push(new Date(chartCandles[chartCandles.length - 1].t));
            for (const row of payload.priceDemo) {
                if (row.t) dates.push(new Date(row.t));
            }
            const valid = dates.filter(date => !Number.isNaN(date.getTime()));
            return valid.length ? new Date(Math.max(...valid.map(date => date.getTime()))) : new Date();
        }

        function xRangeEndDate() {
            const dates = [latestObservedDate()];
            for (const row of payload.forecasts) {
                dates.push(new Date(forecastTimestamp(row)));
            }
            const valid = dates.filter(date => !Number.isNaN(date.getTime()));
            const end = valid.length ? new Date(Math.max(...valid.map(date => date.getTime()))) : new Date();
            const config = currentRange();
            if (!config.days) return end;
            const oneHour = 60 * 60 * 1000;
            const oneDay = 24 * oneHour;
            const pad = Math.min(Math.max(config.days * oneDay * 0.04, 2 * oneHour), 18 * oneHour);
            return new Date(end.getTime() + pad);
        }

        function rangeStartDate() {
            const config = currentRange();
            if (!config.days) return null;
            const end = latestObservedDate();
            return new Date(end.getTime() - config.days * 24 * 60 * 60 * 1000);
        }

        function filteredDemoRows() {
            if (selectedRange === "All") return payload.priceDemo;
            const start = rangeStartDate();
            if (!start) return payload.priceDemo;
            return payload.priceDemo.filter(row => {
                const date = new Date(row.t);
                return !Number.isNaN(date.getTime()) && date >= start;
            });
        }

        function actualRowsForChart() {
            if (selectedRange !== "All" && chartCandles.length > 0) {
                return chartCandles;
            }
            return filteredDemoRows().map(row => ({ t: row.t, actual: row.actual }));
        }

        function forecastRowsForRange() {
            if (selectedRange === "All") return payload.forecasts;
            const start = rangeStartDate();
            if (!start) return payload.forecasts;
            const end = xRangeEndDate();
            end.setHours(23, 59, 59, 999);
            return payload.forecasts.filter(row => {
                const date = new Date(forecastTimestamp(row));
                return !Number.isNaN(date.getTime()) && date >= start && date <= end;
            });
        }

        function renderRangeButtons() {
            const container = document.getElementById("forecast-range-buttons");
            container.innerHTML = rangeOptions().map(item => `
                <button class="range-btn ${item.label === selectedRange ? "active" : ""}" type="button" data-range="${item.label}">
                    ${item.label}
                </button>
            `).join("");
            container.querySelectorAll("button").forEach(button => {
                button.addEventListener("click", () => {
                    selectedRange = button.dataset.range;
                    renderRangeButtons();
                    fetchChartCandles();
                    renderChart();
                });
            });
        }

        function liveReturn(row) {
            if (live.price === null || row.lastClose === null || live.price <= 0 || row.lastClose <= 0) return null;
            return Math.log(live.price / row.lastClose);
        }

        function liveLoss(row) {
            const ret = liveReturn(row);
            return ret === null ? null : -ret;
        }

        function modelReturn(row) {
            const preferred = numberOrNull(row.returnMedian);
            if (preferred !== null) return preferred;
            const mean = numberOrNull(row.returnMean);
            if (mean !== null) return mean;
            const mu = numberOrNull(row.muReturn);
            if (mu !== null) return mu;
            if (row.predictedClose !== null && row.lastClose !== null && row.predictedClose > 0 && row.lastClose > 0) {
                return Math.log(row.predictedClose / row.lastClose);
            }
            return null;
        }

        function basePrice(row) {
            const livePrice = numberOrNull(live.price);
            if (livePrice !== null) return livePrice;
            return numberOrNull(row.lastClose);
        }

        function realtimeForecastPrice(row) {
            const base = basePrice(row);
            const ret = modelReturn(row);
            if (base !== null && ret !== null) return base * Math.exp(ret);
            return numberOrNull(row.predictedClose);
        }

        function renderCards() {
            const container = document.getElementById("forecast-cards");
            container.innerHTML = payload.forecasts.map(row => {
                const forecastPrice = realtimeForecastPrice(row);
                const forecastDate = forecastDateFor(row);
                return `
                    <article class="card">
                        <div class="card-head">
                            <div class="model">${row.label}</div>
                            <div class="forecast-pill">Forecast ${dateText(forecastDate)}</div>
                        </div>
                        <div class="forecast-price">${money(forecastPrice)}</div>
                        <div class="forecast-caption">Next-day forecast price based on the current live BTC price.</div>
                        <div class="mini-grid">
                            <div class="mini"><span>Current Price</span><strong>${money(basePrice(row))}</strong></div>
                            <div class="mini"><span>Model Return</span><strong>${pct(modelReturn(row))}</strong></div>
                            <div class="mini"><span>Model Base Close</span><strong>${money(row.lastClose)}</strong></div>
                            <div class="mini"><span>Live Return</span><strong>${pct(liveReturn(row))}</strong></div>
                            <div class="mini"><span>VaR 95</span><strong>${pct(row.VaR95)}</strong></div>
                            <div class="mini"><span>CVaR 95</span><strong>${pct(row.CVaR95)}</strong></div>
                            <div class="mini"><span>VaR 99</span><strong>${pct(row.VaR99)}</strong></div>
                            <div class="mini"><span>CVaR 99</span><strong>${pct(row.CVaR99)}</strong></div>
                        </div>
                    </article>
                `;
            }).join("");
        }

        function renderTable() {
            const body = document.getElementById("forecast-table-body");
            body.innerHTML = payload.forecasts.map(row => {
                const forecastPrice = realtimeForecastPrice(row);
                return `
                    <tr>
                        <td>${row.label}</td>
                        <td>${dateText(forecastDateFor(row))}</td>
                        <td>${money(basePrice(row))}</td>
                        <td>${money(forecastPrice)}</td>
                        <td>${pct(modelReturn(row))}</td>
                        <td>${pct(liveReturn(row))}</td>
                        <td>${pct(row.VaR95)}</td>
                        <td>${pct(row.CVaR95)}</td>
                        <td>${pct(row.VaR99)}</td>
                        <td>${pct(row.CVaR99)}</td>
                    </tr>
                `;
            }).join("");
        }

        function yAxisRangeFromTraces(traces) {
            const values = [];
            for (const trace of traces) {
                if (!Array.isArray(trace.y)) continue;
                for (const value of trace.y) {
                    const parsed = numberOrNull(value);
                    if (parsed !== null) values.push(parsed);
                }
            }
            if (!values.length) return undefined;
            const minValue = Math.min(...values);
            const maxValue = Math.max(...values);
            const padding = minValue === maxValue ? Math.max(Math.abs(minValue) * 0.01, 1) : (maxValue - minValue) * 0.08;
            return [Math.max(0, minValue - padding), maxValue + padding];
        }

        function chartGuides(nowX) {
            const forecastX = payload.forecasts.length ? forecastTimestamp(payload.forecasts[0]) : null;
            const shapes = [];
            const annotations = [];

            function addGuide(x, color, label, y) {
                if (!x) return;
                shapes.push({
                    type: "line",
                    xref: "x",
                    yref: "paper",
                    x0: x,
                    x1: x,
                    y0: 0,
                    y1: 1,
                    line: { color, width: 1.5, dash: "dot" },
                });
                annotations.push({
                    x,
                    y,
                    xref: "x",
                    yref: "paper",
                    text: label,
                    showarrow: false,
                    xanchor: "center",
                    yanchor: "bottom",
                    bgcolor: theme.card,
                    bordercolor: color,
                    borderpad: 4,
                    borderwidth: 1,
                    font: { color, size: 12 },
                });
            }

            addGuide(nowX, theme.live, "Current live price", 1.05);
            addGuide(forecastX, theme.primary, "Tomorrow forecast", 1.12);
            return { shapes, annotations };
        }

        function renderChart() {
            if (!window.Plotly) {
                setTimeout(renderChart, 120);
                return;
            }
            const demo = filteredDemoRows();
            const actualRows = actualRowsForChart();
            const traces = [{
                x: actualRows.map(row => row.t),
                y: actualRows.map(row => row.actual),
                mode: "lines",
                name: "Actual Close",
                line: { color: theme.actual, width: 2.4 },
                hovertemplate: "%{x|%Y-%m-%d}<br>Actual: %{y:,.2f} USDT<extra></extra>",
            }];

            for (const model of payload.models) {
                const field = model.key === "SV" ? "sv" : "ms";
                const predictionRows = demo.filter(row => row[field] !== null && row[field] !== undefined);
                if (predictionRows.length > 0) {
                    traces.push({
                        x: predictionRows.map(row => row.t),
                        y: predictionRows.map(row => row[field]),
                        mode: "lines",
                        name: model.label + " Historical Prediction",
                        line: { color: modelColor(model.key), width: 2.1, dash: modelLineDash(model.key) },
                        hovertemplate: "%{x|%Y-%m-%d}<br>Predicted: %{y:,.2f} USDT<extra></extra>",
                    });
                }
            }

            const nowX = currentTimestamp();
            for (const row of forecastRowsForRange()) {
                const forecastPrice = realtimeForecastPrice(row);
                const base = basePrice(row);
                const forecastX = forecastTimestamp(row);
                if (forecastPrice === null || !forecastX) continue;
                if (base !== null) {
                    traces.push({
                        x: [nowX, forecastX],
                        y: [base, forecastPrice],
                        mode: "lines",
                        name: row.label + " Current-to-Forecast Path",
                        line: { color: modelColor(row.model), width: 2.2, dash: "dash" },
                        hovertemplate: "%{x|%Y-%m-%d %H:%M}<br>Path: %{y:,.2f} USDT<extra></extra>",
                    });
                }
                traces.push({
                    x: [forecastX],
                    y: [forecastPrice],
                    mode: "markers",
                    name: row.label + " Tomorrow Forecast",
                    marker: {
                        color: modelColor(row.model),
                        line: { color: theme.text, width: 1 },
                        size: 14,
                        symbol: modelForecastSymbol(row.model),
                    },
                    hovertemplate: "%{x|%Y-%m-%d}<br>Tomorrow Forecast: %{y:,.2f} USDT<extra></extra>",
                });
            }

            if (live.price !== null) {
                traces.push({
                    x: [nowX],
                    y: [live.price],
                    mode: "markers",
                    name: "Current Live BTC Price",
                    marker: { color: theme.live, line: { color: theme.text, width: 1 }, size: 15, symbol: "diamond" },
                    hovertemplate: "%{x|%Y-%m-%d %H:%M}<br>Current: %{y:,.2f} USDT<extra></extra>",
                });
            }

            const configRange = currentRange();
            const xAxisRange = selectedRange === "All" || !configRange.days
                ? undefined
                : [rangeStartDate().toISOString(), xRangeEndDate().toISOString()];
            const yAxisRange = selectedRange === "All" ? undefined : yAxisRangeFromTraces(traces);
            const guides = chartGuides(nowX);

            Plotly.react("forecast-chart", traces, {
                title: { text: "Current BTC Price and Tomorrow Forecast (" + selectedRange + ")", font: { color: theme.text, size: 16 } },
                height: 500,
                margin: { l: 64, r: 24, t: 82, b: 90 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { color: theme.text, family: "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" },
                hovermode: "x unified",
                hoverlabel: {
                    bgcolor: theme.card,
                    bordercolor: theme.border,
                    font: { color: theme.text },
                },
                legend: { orientation: "h", x: 0, y: -0.18, font: { color: theme.text, size: 12 } },
                shapes: guides.shapes,
                annotations: guides.annotations,
                xaxis: { type: "date", range: xAxisRange, gridcolor: theme.grid, tickfont: { color: theme.text } },
                yaxis: {
                    title: { text: "Close Price (USDT)", font: { color: theme.text } },
                    tickprefix: "$",
                    gridcolor: theme.grid,
                    tickfont: { color: theme.text },
                    range: yAxisRange,
                },
            }, config);
        }

        function renderAll() {
            renderCards();
            renderTable();
            renderChart();
        }

        async function fetchTicker() {
            for (const base of restBases) {
                try {
                    const response = await fetch(base + "/api/v3/ticker/24hr?symbol=BTCUSDT", { cache: "no-store" });
                    if (!response.ok) continue;
                    const payload = await response.json();
                    live.price = numberOrNull(payload.lastPrice);
                    live.updatedAt = payload.closeTime;
                    renderAll();
                    return true;
                } catch (error) {}
            }
            return false;
        }

        async function fetchChartCandles() {
            const config = currentRange();
            if (selectedRange === "All" || !config.interval) {
                chartCandles = [];
                renderChart();
                return false;
            }

            const query = `/api/v3/klines?symbol=BTCUSDT&interval=${config.interval}&limit=${config.limit}`;
            for (const base of restBases) {
                try {
                    const response = await fetch(base + query, { cache: "no-store" });
                    if (!response.ok) continue;
                    const rows = await response.json();
                    chartCandles = rows
                        .map(row => ({ t: new Date(row[0]).toISOString(), actual: numberOrNull(row[4]) }))
                        .filter(row => row.actual !== null);
                    renderChart();
                    return true;
                } catch (error) {}
            }
            chartCandles = [];
            renderChart();
            return false;
        }

        function connectStream() {
            clearTimeout(reconnectTimer);
            try {
                ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker");
            } catch (error) {
                scheduleReconnect();
                return;
            }
            ws.onmessage = event => {
                try {
                    const tick = JSON.parse(event.data);
                    live.price = numberOrNull(tick.c);
                    live.updatedAt = tick.E;
                    renderAll();
                } catch (error) {}
            };
            ws.onerror = () => {
                try { ws.close(); } catch (error) {}
            };
            ws.onclose = () => scheduleReconnect();
        }

        function scheduleReconnect() {
            fetchTicker();
            reconnectTimer = setTimeout(connectStream, 3000);
        }

        window.addEventListener("resize", () => {
            const chart = document.getElementById("forecast-chart");
            if (window.Plotly && chart) Plotly.Plots.resize(chart);
        });

        renderRangeButtons();
        renderAll();
        fetchChartCandles();
        fetchTicker();
        connectStream();
        setInterval(fetchTicker, 30000);
        setInterval(fetchChartCandles, 60000);
    </script>
    """

    replacements = {
        "__PRIMARY__": theme["primary"],
        "__CARD__": theme["card"],
        "__TEXT__": theme["text"],
        "__MUTED__": theme["muted"],
        "__BORDER__": theme["border"],
        "__SHADOW__": theme["shadow"],
        "__SUCCESS__": theme["success"],
        "__DANGER__": theme["danger"],
        "__WARNING__": theme["warning"],
        "__PAYLOAD__": payload_json,
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    st.iframe(html, height=980)


def realtime_backtesting_panel(
    btc_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    model: str,
    confidence: str,
) -> None:
    dark_mode = bool(st.session_state.get("dark_theme_enabled", False))
    theme = {
        "primary": "#7aa2ff" if dark_mode else "#2f5fda",
        "card": "#121c2f" if dark_mode else "#ffffff",
        "text": "#e7edf7" if dark_mode else "#101828",
        "muted": "#9aa8bd" if dark_mode else "#667085",
        "border": "rgba(122, 162, 255, 0.30)" if dark_mode else "rgba(47, 95, 218, 0.20)",
        "grid": "rgba(168, 180, 199, 0.22)" if dark_mode else "rgba(148, 163, 184, 0.28)",
        "shadow": "rgba(0, 0, 0, 0.35)" if dark_mode else "rgba(16, 24, 40, 0.07)",
        "loss": "#8290a3" if dark_mode else "#5b677a",
        "breach": "#fb7185" if dark_mode else "#b4234a",
        "ms": "#38bdf8" if dark_mode else "#0f7f8f",
        "sv": "#a78bfa" if dark_mode else "#6d5bd0",
    }
    payload = {
        "btc": _btc_chart_records(btc_df),
        "risk": _risk_chart_records(risk_df, model, confidence),
        "models": _chart_models(model),
        "confidence": confidence,
        "theme": theme,
    }
    payload_json = json.dumps(payload, allow_nan=False)

    html = """
    <div class="bt-wrap">
        <div id="metric-cards" class="metric-grid"></div>
        <div class="chart-grid">
            <section class="panel"><div id="bt-risk-chart" class="chart"></div></section>
            <section class="panel"><div id="bt-breach-chart" class="chart"></div></section>
        </div>
    </div>

    <style>
        :root {
            --primary: __PRIMARY__;
            --card: __CARD__;
            --text: __TEXT__;
            --muted: __MUTED__;
            --border: __BORDER__;
            --shadow: __SHADOW__;
        }
        * { box-sizing: border-box; letter-spacing: 0; }
        body {
            background: transparent;
            color: var(--text);
            font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;
            margin: 0;
            overflow: visible;
        }
        .bt-wrap {
            display: grid;
            gap: 1rem;
            padding-bottom: 1rem;
        }
        .metric-grid {
            display: grid;
            gap: 0.8rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }
        .metric {
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--primary) 7%, var(--card)) 0%, var(--card) 72%);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: 12px;
            box-shadow: 0 10px 24px var(--shadow);
            min-height: 108px;
            padding: 0.9rem 0.95rem;
        }
        .metric span {
            color: var(--muted);
            display: block;
            font-size: 0.76rem;
            font-weight: 820;
            margin-bottom: 0.35rem;
        }
        .metric strong {
            color: var(--text);
            display: block;
            font-size: clamp(1.35rem, 2.6vw, 2rem);
            font-weight: 860;
        }
        .chart-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .panel {
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--primary) 7%, var(--card)) 0%, var(--card) 72%);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 12px 28px var(--shadow);
            overflow: visible;
            padding: 0.65rem;
        }
        .chart {
            height: 540px;
            width: 100%;
        }
        @media (max-width: 980px) {
            .metric-grid,
            .chart-grid { grid-template-columns: 1fr; }
        }
    </style>

    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <script>
        const payload = __PAYLOAD__;
        const theme = payload.theme;
        const config = { displayModeBar: false, responsive: true };
        const restBases = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://data-api.binance.vision",
        ];
        let btcRows = payload.btc.map(normalizeBtc).filter(row => row.t !== null);
        const riskRows = payload.risk.map(normalizeRisk).filter(row => row.t !== null);
        let ws = null;
        let reconnectTimer = null;

        function num(value) {
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : null;
        }

        function normalizeBtc(row) {
            return { t: toMs(row.t), close: num(row.close), ret: num(row.ret), loss: num(row.loss) };
        }

        function normalizeRisk(row) {
            const normalized = { t: toMs(row.t), actual_loss: num(row.actual_loss) };
            for (const key of Object.keys(row)) {
                if (key !== "t" && key !== "actual_loss") normalized[key] = num(row[key]);
            }
            return normalized;
        }

        function toMs(value) {
            if (!value) return null;
            const parsed = new Date(value).getTime();
            return Number.isFinite(parsed) ? parsed : null;
        }

        function iso(ms) {
            return new Date(ms).toISOString();
        }

        function dayKey(ms) {
            return new Date(ms).toISOString().slice(0, 10);
        }

        function utcDayStart(ms) {
            const date = new Date(ms);
            return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        }

        function pct(value) {
            const parsed = num(value);
            return parsed === null ? "N/A" : (parsed * 100).toFixed(2) + "%";
        }

        function numberText(value, digits = 2) {
            const parsed = num(value);
            return parsed === null ? "N/A" : parsed.toFixed(digits);
        }

        function erfc(x) {
            const z = Math.abs(x);
            const t = 1 / (1 + z / 2);
            const r = t * Math.exp(
                -z * z - 1.26551223 + t * (
                    1.00002368 + t * (
                        0.37409196 + t * (
                            0.09678418 + t * (
                                -0.18628806 + t * (
                                    0.27886807 + t * (
                                        -1.13520398 + t * (
                                            1.48851587 + t * (
                                                -0.82215223 + t * 0.17087277
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            );
            return x >= 0 ? r : 2 - r;
        }

        function modelColor(model) {
            return model.key === "SV" ? theme.sv : theme.ms;
        }

        function latestThreshold(model, field) {
            const column = model.key + "_" + field;
            let latest = null;
            for (const row of riskRows) {
                if (row[column] !== null) latest = { t: row.t, value: row[column] };
            }
            return latest;
        }

        function mergeBtcRows(incoming) {
            const byDay = new Map();
            for (const row of btcRows) byDay.set(dayKey(row.t), row);
            for (const row of incoming) byDay.set(dayKey(row.t), { ...(byDay.get(dayKey(row.t)) || {}), ...row });
            btcRows = recomputeReturns([...byDay.values()].sort((a, b) => a.t - b.t));
        }

        function recomputeReturns(rows) {
            let prevClose = null;
            for (const row of rows) {
                if (row.close !== null && prevClose !== null && row.close > 0 && prevClose > 0) {
                    row.ret = Math.log(row.close / prevClose);
                    row.loss = -row.ret;
                }
                if (row.close !== null) prevClose = row.close;
            }
            return rows;
        }

        function seriesForModel(model) {
            const varCol = model.key + "_VaR";
            const rowsByDay = new Map();
            for (const row of riskRows) {
                if (row.actual_loss !== null && row[varCol] !== null) {
                    rowsByDay.set(dayKey(row.t), { t: row.t, loss: row.actual_loss, varValue: row[varCol] });
                }
            }
            const latest = btcRows[btcRows.length - 1];
            const threshold = latestThreshold(model, "VaR");
            if (latest && latest.loss !== null && threshold) {
                rowsByDay.set(dayKey(latest.t), { t: latest.t, loss: latest.loss, varValue: threshold.value, live: true });
            }
            return [...rowsByDay.values()].sort((a, b) => a.t - b.t);
        }

        function kupiecPValue(n, x) {
            if (!n) return null;
            const p = 1 - Number(payload.confidence) / 100;
            const phat = x / n;
            if (phat <= 0 || phat >= 1) return null;
            const llNull = (n - x) * Math.log(1 - p) + x * Math.log(p);
            const llAlt = (n - x) * Math.log(1 - phat) + x * Math.log(phat);
            const lr = Math.max(0, -2 * (llNull - llAlt));
            return erfc(Math.sqrt(lr / 2));
        }

        function christoffersenPValue(breaches) {
            if (breaches.length < 2) return null;
            let n00 = 0, n01 = 0, n10 = 0, n11 = 0;
            for (let i = 1; i < breaches.length; i += 1) {
                const prev = breaches[i - 1], cur = breaches[i];
                if (!prev && !cur) n00 += 1;
                if (!prev && cur) n01 += 1;
                if (prev && !cur) n10 += 1;
                if (prev && cur) n11 += 1;
            }
            const total = n00 + n01 + n10 + n11;
            if (!total) return null;
            const pi = (n01 + n11) / total;
            const pi01 = (n00 + n01) ? n01 / (n00 + n01) : 0;
            const pi11 = (n10 + n11) ? n11 / (n10 + n11) : 0;
            function term(count, prob) {
                if (!count) return 0;
                if (prob <= 0 || prob >= 1) return 0;
                return count * Math.log(prob);
            }
            const llNull = term(n00 + n10, 1 - pi) + term(n01 + n11, pi);
            const llAlt = term(n00, 1 - pi01) + term(n01, pi01) + term(n10, 1 - pi11) + term(n11, pi11);
            const lr = Math.max(0, -2 * (llNull - llAlt));
            return erfc(Math.sqrt(lr / 2));
        }

        function metricsForModel(model) {
            const rows = seriesForModel(model);
            const breaches = rows.map(row => row.loss > row.varValue);
            const n = breaches.length;
            const x = breaches.filter(Boolean).length;
            return {
                model,
                n,
                expected: n * (1 - Number(payload.confidence) / 100),
                breachCount: x,
                breachRate: n ? x / n : null,
                kupiec: kupiecPValue(n, x),
                christoffersen: christoffersenPValue(breaches),
            };
        }

        function renderMetrics() {
            const metrics = payload.models.map(metricsForModel);
            const cards = [];
            for (const item of metrics) {
                cards.push(
                    ["Model", item.model.label],
                    ["Observations", numberText(item.n, 0)],
                    ["Expected Breaches", numberText(item.expected, 2)],
                    ["Breach Count", numberText(item.breachCount, 0)],
                    ["Breach Rate", pct(item.breachRate)],
                    ["Kupiec p-value", numberText(item.kupiec, 4)],
                    ["Christoffersen p-value", numberText(item.christoffersen, 4)],
                );
            }
            document.getElementById("metric-cards").innerHTML = cards.map(([label, value]) => `
                <div class="metric"><span>${label}</span><strong>${value}</strong></div>
            `).join("");
        }

        function baseLayout(title, yTitle) {
            return {
                title: { text: title, font: { color: theme.text, size: 18 } },
                height: 540,
                margin: { l: 64, r: 28, t: 68, b: 96 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { color: theme.text, family: "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" },
                hovermode: "x unified",
                hoverlabel: {
                    bgcolor: theme.card,
                    bordercolor: theme.border,
                    font: { color: theme.text },
                },
                legend: { orientation: "h", x: 0, y: -0.2, font: { color: theme.text, size: 12 } },
                xaxis: { type: "date", gridcolor: theme.grid, tickfont: { color: theme.text } },
                yaxis: {
                    title: { text: yTitle, font: { color: theme.text } },
                    tickformat: ".1%",
                    gridcolor: theme.grid,
                    tickfont: { color: theme.text },
                },
            };
        }

        function renderCharts() {
            if (!window.Plotly) {
                setTimeout(renderCharts, 120);
                return;
            }
            const lossTraces = [];
            const breachTraces = [];
            for (const model of payload.models) {
                const rows = seriesForModel(model);
                lossTraces.push(
                    {
                        x: rows.map(row => iso(row.t)),
                        y: rows.map(row => row.loss),
                        mode: "lines",
                        name: "Realized Loss",
                        line: { color: theme.loss, width: 1.4 },
                        hovertemplate: "%{x|%Y-%m-%d}<br>Loss: %{y:.4%}<extra></extra>",
                    },
                    {
                        x: rows.map(row => iso(row.t)),
                        y: rows.map(row => row.varValue),
                        mode: "lines",
                        name: model.label + " VaR " + payload.confidence + "%",
                        line: { color: modelColor(model), width: 2 },
                        hovertemplate: "%{x|%Y-%m-%d}<br>VaR: %{y:.4%}<extra></extra>",
                    },
                );
                breachTraces.push({
                    x: rows.map(row => iso(row.t)),
                    y: rows.map(row => row.loss > row.varValue ? 1 : 0),
                    type: "bar",
                    name: model.label + " Breach",
                    marker: { color: rows.map(row => row.loss > row.varValue ? theme.breach : "rgba(148,163,184,0.25)") },
                    hovertemplate: "%{x|%Y-%m-%d}<br>Breach: %{y}<extra></extra>",
                });
            }
            Plotly.react("bt-risk-chart", lossTraces, baseLayout("Live Realized Loss vs VaR " + payload.confidence + "%", "Loss / VaR"), config);
            const breachLayout = baseLayout("Live VaR Breach Events " + payload.confidence + "%", "Breach Indicator");
            breachLayout.yaxis.tickmode = "array";
            breachLayout.yaxis.tickvals = [0, 1];
            breachLayout.yaxis.range = [0, 1.15];
            Plotly.react("bt-breach-chart", breachTraces, breachLayout, config);
        }

        function renderAll() {
            renderMetrics();
            renderCharts();
        }

        async function fetchDailyCandles() {
            for (const base of restBases) {
                try {
                    const response = await fetch(base + "/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=120", { cache: "no-store" });
                    if (!response.ok) continue;
                    const payload = await response.json();
                    mergeBtcRows(payload.map(row => ({ t: Number(row[0]), close: num(row[4]) })));
                    renderAll();
                    return true;
                } catch (error) {}
            }
            return false;
        }

        function updateLivePrice(price, eventTime) {
            const livePrice = num(price);
            const liveTime = num(eventTime) || Date.now();
            if (livePrice === null) return;
            mergeBtcRows([{ t: utcDayStart(liveTime), close: livePrice }]);
            renderAll();
        }

        function connectStream() {
            clearTimeout(reconnectTimer);
            try {
                ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker");
            } catch (error) {
                scheduleReconnect();
                return;
            }
            ws.onmessage = event => {
                try {
                    const tick = JSON.parse(event.data);
                    updateLivePrice(tick.c, tick.E);
                } catch (error) {}
            };
            ws.onerror = () => {
                try { ws.close(); } catch (error) {}
            };
            ws.onclose = () => scheduleReconnect();
        }

        function scheduleReconnect() {
            fetchDailyCandles();
            reconnectTimer = setTimeout(connectStream, 3000);
        }

        window.addEventListener("resize", () => {
            for (const id of ["bt-risk-chart", "bt-breach-chart"]) {
                const element = document.getElementById(id);
                if (window.Plotly && element) Plotly.Plots.resize(element);
            }
        });

        btcRows = recomputeReturns(btcRows.sort((a, b) => a.t - b.t));
        renderAll();
        fetchDailyCandles();
        connectStream();
        setInterval(fetchDailyCandles, 60000);
    </script>
    """

    replacements = {
        "__PRIMARY__": theme["primary"],
        "__CARD__": theme["card"],
        "__TEXT__": theme["text"],
        "__MUTED__": theme["muted"],
        "__BORDER__": theme["border"],
        "__SHADOW__": theme["shadow"],
        "__PAYLOAD__": payload_json,
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    st.iframe(html, height=1180)


def metric_grid(items: list[dict[str, Any]], columns_per_row: int = 3) -> None:
    if not items:
        return

    for start in range(0, len(items), columns_per_row):
        row_items = items[start : start + columns_per_row]
        cols = st.columns(len(row_items))
        for col, item in zip(cols, row_items):
            col.markdown(_metric_card_html(item), unsafe_allow_html=True)


def info_card(label: str, value: str, caption: str | None = None) -> None:
    caption_html = f"<div class='small-note'>{caption}</div>" if caption else ""
    st.markdown(
        f"""
        <div class="thesis-card">
            <div class="thesis-card-label">{label}</div>
            <div class="thesis-card-value">{value}</div>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str) -> None:
    st.markdown(f"<div class='small-note'>{text}</div>", unsafe_allow_html=True)


def warn_missing(filename: str, detail: str | None = None) -> None:
    message = f"Missing output file: `{filename}`."
    if detail:
        message = f"{message} {detail}"
    st.warning(message)


def warn_missing_many(filenames: list[str]) -> None:
    if filenames:
        joined = ", ".join(f"`{filename}`" for filename in filenames)
        st.warning(f"Some optional output files are not available: {joined}.")


def render_table(
    df: pd.DataFrame,
    title: str | None = None,
    missing_label: str = "This table is not available.",
    height: int | None = None,
) -> None:
    if title:
        st.subheader(title)
    if df.empty:
        st.warning(missing_label)
        return

    display = tidy_dataframe(df)
    max_height = f"{height}px" if height is not None else "420px"
    st.markdown(_html_table(display, max_height), unsafe_allow_html=True)


def _html_table(df: pd.DataFrame, max_height: str) -> str:
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in df.columns)
    numeric_columns = {
        column for column in df.columns if pd.api.types.is_numeric_dtype(df[column])
    }
    rows: list[str] = []

    for _, row in df.iterrows():
        cells: list[str] = []
        for column in df.columns:
            css_class = "numeric-cell" if column in numeric_columns else ""
            cells.append(f"<td class='{css_class}'>{escape(_display_cell(row[column]))}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return f"""
    <div class="bitrisk-table-wrap" style="--bitrisk-table-height: {escape(max_height)};">
        <div class="bitrisk-table-scroll">
            <table class="bitrisk-table">
                <thead><tr>{headers}</tr></thead>
                <tbody>{"".join(rows)}</tbody>
            </table>
        </div>
    </div>
    """


def _display_cell(value: Any) -> str:
    if value is None:
        return "N/A"
    try:
        if bool(pd.isna(value)):
            return "N/A"
    except (TypeError, ValueError):
        pass
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def render_plotly(fig: Any) -> None:
    _apply_plotly_theme(fig, dark_mode=bool(st.session_state.get("dark_theme_enabled", False)))
    st.plotly_chart(
        fig,
        width="stretch",
        theme="streamlit",
        config={"displayModeBar": False, "responsive": True},
    )


def status_message(label: str, passed: bool | None) -> None:
    if passed is None:
        st.info(f"{label}: N/A")
    elif passed:
        st.success(f"{label}: Pass")
    else:
        st.error(f"{label}: Fail")


def _apply_plotly_theme(fig: Any, dark_mode: bool) -> None:
    if not hasattr(fig, "update_layout"):
        return

    if dark_mode:
        text_color = "#e5eefb"
        muted_color = "rgba(168, 180, 199, 0.38)"
        hover_bg = "#111c2e"
        hover_border = "rgba(96, 165, 250, 0.45)"
    else:
        text_color = "#0f172a"
        muted_color = "rgba(148, 163, 184, 0.28)"
        hover_bg = "#ffffff"
        hover_border = "rgba(47, 95, 218, 0.26)"

    fig.update_layout(
        font={"color": text_color, "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"},
        title={"font": {"color": text_color}},
        legend={"font": {"color": text_color}},
        hoverlabel={
            "bgcolor": hover_bg,
            "bordercolor": hover_border,
            "font": {"color": text_color},
        },
    )
    fig.update_xaxes(gridcolor=muted_color, zerolinecolor=muted_color, tickfont={"color": text_color})
    fig.update_yaxes(gridcolor=muted_color, zerolinecolor=muted_color, tickfont={"color": text_color})


def _metric_card_html(item: dict[str, Any]) -> str:
    label = str(item.get("label", ""))
    value = str(item.get("value", "N/A"))
    delta = item.get("delta")
    help_text = item.get("help")
    accent = item.get("accent") or _accent_for_metric(label, value)

    title_attr = f' title="{escape(str(help_text), quote=True)}"' if help_text else ""
    delta_html = ""
    if delta is not None:
        delta_html = f"<div class='metric-card-delta'>{escape(str(delta))}</div>"

    return f"""
    <div class="metric-card metric-accent-{escape(accent)}"{title_attr}>
        <div class="metric-card-label">{escape(label)}</div>
        <div class="metric-card-value">{escape(value)}</div>
        {delta_html}
    </div>
    """


def _forecast_records(df: pd.DataFrame, model: str) -> list[dict[str, Any]]:
    if df.empty or "model" not in df.columns:
        return []

    model_keys = [item["key"] for item in _chart_models(model)]
    table = df[df["model"].astype(str).str.upper().isin(model_keys)].copy()
    records: list[dict[str, Any]] = []
    for _, row in table.iterrows():
        model_key = str(row.get("model", "")).upper()
        predicted_close = _to_float(row.get("predicted_close_median_sim"))
        if predicted_close is None:
            predicted_close = _to_float(row.get("predicted_close_mu"))
        records.append(
            {
                "model": model_key,
                "label": _chart_model_label(model_key),
                "forecastDate": _date_iso(row.get("forecast_date")),
                "lastClose": _to_float(row.get("last_close")),
                "predictedClose": predicted_close,
                "muReturn": _to_float(row.get("mu_return")),
                "returnMean": _to_float(row.get("return_mean_sim")),
                "returnMedian": _to_float(row.get("return_median_sim")),
                "VaR95": _to_float(row.get("VaR_95")),
                "CVaR95": _to_float(row.get("CVaR_95")),
                "VaR99": _to_float(row.get("VaR_99")),
                "CVaR99": _to_float(row.get("CVaR_99")),
                "pHigh": _to_float(row.get("p_high_state")),
                "priceAtVaR95": _to_float(row.get("price_at_VaR_95")),
                "priceAtVaR99": _to_float(row.get("price_at_VaR_99")),
            }
        )
    return records


def _price_demo_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty or "open_time" not in df.columns:
        return []

    records: list[dict[str, Any]] = []
    for _, row in df.sort_values("open_time").iterrows():
        date_value = _date_iso(row.get("open_time"))
        if date_value is None:
            continue
        records.append(
            {
                "t": date_value,
                "actual": _to_float(row.get("close_actual")),
                "ms": _to_float(row.get("close_pred_ms")),
                "sv": _to_float(row.get("close_pred_sv")),
            }
        )
    return records


def _btc_chart_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty or "open_time" not in df.columns:
        return []

    records: list[dict[str, Any]] = []
    for _, row in df.sort_values("open_time").iterrows():
        date_value = _date_iso(row.get("open_time"))
        if date_value is None:
            continue
        ret = _to_float(row.get("ret_log"))
        loss = _to_float(row.get("loss"))
        if loss is None and ret is not None:
            loss = -ret
        records.append(
            {
                "t": date_value,
                "close": _to_float(row.get("close")),
                "ret": ret,
                "loss": loss,
                "vol": _to_float(row.get("rolling_vol_30d")),
            }
        )
    return records


def _risk_chart_records(df: pd.DataFrame, model: str, confidence: str) -> list[dict[str, Any]]:
    if df.empty or "open_time" not in df.columns:
        return []

    model_keys = [item["key"] for item in _chart_models(model)]
    records: list[dict[str, Any]] = []
    for _, row in df.sort_values("open_time").iterrows():
        date_value = _date_iso(row.get("open_time"))
        if date_value is None:
            continue
        record: dict[str, Any] = {
            "t": date_value,
            "actual_loss": _to_float(row.get("actual_loss")),
            "MS_GARCH_p_high": _to_float(row.get("MS_GARCH_p_high")),
        }
        for model_key in model_keys:
            record[f"{model_key}_sigma"] = _to_float(row.get(f"{model_key}_sigma"))
            record[f"{model_key}_VaR"] = _to_float(row.get(f"{model_key}_VaR_{confidence}"))
            record[f"{model_key}_CVaR"] = _to_float(row.get(f"{model_key}_CVaR_{confidence}"))
        records.append(record)
    return records


def _chart_models(model: str) -> list[dict[str, str]]:
    keys = ["MS_GARCH", "SV"] if model == "COMPARE" else [model]
    return [{"key": key, "label": _chart_model_label(key)} for key in keys if key in {"MS_GARCH", "SV"}]


def _chart_model_label(model_key: str) -> str:
    labels = {
        "MS_GARCH": "MS-GARCH",
        "SV": "Stochastic Volatility",
    }
    return labels.get(model_key, model_key)


def _date_iso(value: Any) -> str | None:
    if _missing(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return parsed.isoformat()


def _format_usd(value: Any) -> str:
    if _missing(value):
        return "N/A"
    return f"${float(value):,.2f}"


def _to_float(value: Any) -> float | None:
    if _missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_signed_percent(value: Any) -> str:
    if _missing(value):
        return "N/A"
    numeric = float(value)
    sign = "+" if numeric >= 0 else ""
    return f"{sign}{numeric * 100:,.2f}% (24h)"


def _format_number(value: Any) -> str:
    if _missing(value):
        return "N/A"
    return f"{float(value):,.2f}"


def _format_compact_usd(value: Any) -> str:
    if _missing(value):
        return "N/A"
    numeric = float(value)
    abs_value = abs(numeric)
    if abs_value >= 1_000_000_000:
        return f"${numeric / 1_000_000_000:,.2f}B"
    if abs_value >= 1_000_000:
        return f"${numeric / 1_000_000:,.2f}M"
    if abs_value >= 1_000:
        return f"${numeric / 1_000:,.2f}K"
    return f"${numeric:,.2f}"


def _is_negative(value: Any) -> bool:
    if _missing(value):
        return False
    return float(value) < 0


def _missing(value: Any) -> bool:
    return value is None or pd.isna(value)


def _accent_for_metric(label: str, value: str) -> str:
    text = f"{label} {value}".lower()
    if "breach" in text:
        return "red" if "no breach" not in text else "green"
    if "btc" in text or "close" in text or "price" in text:
        return "blue"
    if "return" in text:
        return "slate"
    if "volatility" in text or "sigma" in text:
        return "cyan"
    if "cvar" in text:
        return "amber"
    if "var" in text:
        return "red"
    if "probability" in text or "state" in text:
        return "purple"
    if "pass" in text:
        return "green"
    return "blue"

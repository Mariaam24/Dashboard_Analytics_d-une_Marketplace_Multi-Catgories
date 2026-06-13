"""
config.py — Configuration centrale : couleurs, thème Plotly, chemins.
"""

import os

# ─────────────────────────────────────────
# CHEMINS
# ─────────────────────────────────────────
# BASE_DIR = racine du projet (parent de dashboard/)
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "silver_orders.csv")

# ─────────────────────────────────────────
# COULEURS
# ─────────────────────────────────────────
COLOR_PRIMARY = "#2563eb"
COLOR_ACCENT  = "#f59e0b"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER  = "#ef4444"

COLOR_SEQ = [
    "#2563eb", "#f59e0b", "#10b981", "#ef4444",
    "#8b5cf6", "#06b6d4", "#f97316", "#84cc16",
    "#ec4899", "#6366f1"
]

# ─────────────────────────────────────────
# THÈME PLOTLY
# ─────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    font_family   = "DM Sans",
    font_color    = "#374151",
    paper_bgcolor = "white",
    plot_bgcolor  = "white",
    margin        = dict(t=30, b=30, l=20, r=20),
    xaxis         = dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb"),
    yaxis         = dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb"),
)

# ─────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────
GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    [data-testid="stSidebar"] {
        background-color: #0f1117;
        border-right: 1px solid #1e2130;
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .main-header {
        font-size: 28px; font-weight: 600;
        color: #1a1a2e; letter-spacing: -0.5px; margin-bottom: 4px;
    }
    .main-subtitle {
        font-size: 13px; color: #6b7280;
        margin-bottom: 24px; font-weight: 400;
    }
    .section-title {
        font-size: 12px; font-weight: 600; color: #374151;
        text-transform: uppercase; letter-spacing: 0.6px;
        margin-bottom: 12px; padding-bottom: 8px;
        border-bottom: 1px solid #f3f4f6;
    }
    .sidebar-brand {
        font-size: 16px; font-weight: 600;
        color: white; letter-spacing: -0.3px; margin-bottom: 4px;
    }
    .sidebar-brand-sub { font-size: 11px; color: #6b7280; margin-bottom: 24px; }
    .filter-label {
        font-size: 11px; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.6px;
        color: #9ca3af; margin-bottom: 4px;
    }
    .stApp { background-color: #f9fafb; }
    [data-testid="metric-container"] {
        background: white; border: 1px solid #e5e7eb;
        border-radius: 8px; padding: 16px 20px;
    }
    hr { border: none; border-top: 1px solid #f3f4f6; margin: 20px 0; }
</style>
"""
"""
config.py — Configuration centrale
"""

import os

# =========================================================
# BASE DIR
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# =========================================================
# DUCKDB PATH
# =========================================================

DB_PATH = r"C:\Users\HP\Desktop\olist_project_V2\olist_dbt\dev.duckdb"

# =========================================================
# COLORS
# =========================================================

COLOR_PRIMARY = "#2563eb"
COLOR_ACCENT  = "#f59e0b"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER  = "#ef4444"

COLOR_SEQ = [
    "#2563eb",
    "#f59e0b",
    "#10b981",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#f97316",
    "#84cc16",
    "#ec4899",
    "#6366f1"
]

# =========================================================
# PLOTLY THEME
# =========================================================

PLOTLY_LAYOUT = dict(
    font_family="DM Sans",
    font_color="#374151",
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(t=30, b=30, l=20, r=20),

    xaxis=dict(
        showgrid=True,
        gridcolor="#f3f4f6",
        linecolor="#e5e7eb"
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#f3f4f6",
        linecolor="#e5e7eb"
    ),
)

# =========================================================
# GLOBAL CSS
# =========================================================

GLOBAL_CSS = """
<style>

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #f9fafb;
}

[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px 20px;
}

</style>
"""
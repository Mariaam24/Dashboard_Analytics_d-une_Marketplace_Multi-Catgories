from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

# Point to the populated dbt database
DB_PATH = (BASE_DIR / "My_dbt_project" / "data" / "ecommerce.duckdb").resolve()

# COLORS
COLOR_PRIMARY = "#2563eb"
COLOR_ACCENT = "#f59e0b"

COLOR_SEQ = [
    "#2563eb", "#f59e0b", "#10b981", "#ef4444",
    "#8b5cf6", "#06b6d4", "#f97316", "#84cc16"
]

# PLOTLY
PLOTLY_LAYOUT = dict(
    font_family="DM Sans",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=30, b=30, l=20, r=20)
)

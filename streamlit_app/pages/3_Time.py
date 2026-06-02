import streamlit as st
import plotly.express as px
from utils import get_data

df = get_data("""
SELECT d.year, d.month, SUM(f.revenue) AS revenue
FROM fact_orders f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month
""")

st.title("📅 Seasonality")

fig = px.line(df, x="month", y="revenue", color="year")
st.plotly_chart(fig)
import streamlit as st
import plotly.express as px
from utils import get_data

df = get_data("""
SELECT r.region_name, SUM(f.revenue) AS revenue
FROM fact_orders f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region_name
""")

st.title("🌍 Geography")

fig = px.pie(df, names="region_name", values="revenue")
st.plotly_chart(fig)
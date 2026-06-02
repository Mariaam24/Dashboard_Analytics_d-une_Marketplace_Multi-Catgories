import streamlit as st
import plotly.express as px
from utils import get_data

df = get_data("""
SELECT 
    p.category,
    SUM(f.revenue) AS revenue
FROM fact_orders f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC
""")

st.title("🛍️ Top Products")

fig = px.bar(df, x="category", y="revenue")
st.plotly_chart(fig)
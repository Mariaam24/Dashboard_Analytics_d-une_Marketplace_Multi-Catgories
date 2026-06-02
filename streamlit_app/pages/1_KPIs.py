import streamlit as st
from utils import get_data

df = get_data("""
SELECT 
    SUM(total_revenue) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS items
FROM fact_orders
""")

st.title("📊 Executive KPIs")

st.metric("Revenue", df["revenue"][0])
st.metric("Orders", df["orders"][0])
st.metric("Items Sold", df["items"][0])
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/postgres"
)

def get_data(query):
    return pd.read_sql(query, engine)
import sqlite3
import pandas as pd

conn = sqlite3.connect("/Users/admin/Desktop/tg_bot/fribot/kitbot.db")

# tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
pd.set_option("display.max_columns", None)
df = pd.read_sql_query("SELECT * FROM recipes", conn)
print(df.head())


tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print(tables)

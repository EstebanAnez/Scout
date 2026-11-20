import pandas as pd
import sqlite3
from langchain.tools import tool

@tool
def get_expense_value(country):
    """
    Use this tool ONLY when the user asks for the expenses of the company for a specific
    country. Do not use this tool if the user is asking about multiple countries.
    """
    print("The agent is using get_expense_value tool")

    data = pd.read_csv("tool_files/The Keepsake expenses.csv")

    if country not in data['country'].values:
        return f"Invalid country name {country}"

    value = data.loc[data['country'] == country, 'expenses']

    return float(value.iloc[0])

@tool
def combine_expenses(country1, country2):
    """
    Use this tool ONLY when asked to combine expenses for EXACTLY two countries.
    ALWAYS use this tool when asked to add expenses for two countries.
    """
    print("The agent is using combine_expenses tool")

    data = pd.read_csv("tool_files/The Keepsake expenses.csv")

    if country1 not in data['country'].values:
        return f"Invalid country name {country1}"

    if country2 not in data['country'].values:
        return f"Invalid country name {country2}"

    value1 = data.loc[data['country'] == country1, 'expenses']
    value2 = data.loc[data['country'] == country2, 'expenses']

    return float(value1.iloc[0]) + float(value2.iloc[0])

@tool
def query_transactions(sql_query: str):
    """
    Use this tool when the user asks questions that require querying transaction data.
    The tool executes a SQLite query on the company database and returns the results.
    The database has one table called raw_transactions with these columns:
    - InvoiceNo (TEXT)
    - StockCode (TEXT)
    - Description (TEXT)
    - Quantity (INTEGER)
    - InvoiceDate (TIMESTAMP)
    - UnitPrice (REAL)
    - CustomerID (REAL)
    - Country (TEXT)
    - LineRevenue (REAL)
    Only SELECT queries are allowed.
    """
    print("The agent is using query_transactions tool")
    print(sql_query)

    if not sql_query.strip().upper().startswith("SELECT"):
        return "Only SELECT queries are allowed."

    # open the database read only, so even a bad query can never change the data
    conn = sqlite3.connect("file:tool_files/company.db?mode=ro", uri=True)
    try:
        df = pd.read_sql_query(sql_query, conn)
        return df.to_string(index=False)
    except Exception as e:
        return f"Query error: {str(e)}"
    finally:
        conn.close()

@tool
def calculate_profit(revenue: float, expenses: float):
    """
    Use this tool ONLY when the user asks for profit and you already have both
    revenue and expenses values.

    Profit = revenue - expenses.

    ALWAYS use this tool after first retrieving revenue from the transaction
    data and expenses from the expense lookup tool. Do not guess values.
    """
    print("The agent is using calculate_profit tool")

    return float(revenue) - float(expenses)
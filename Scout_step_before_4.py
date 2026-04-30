# agent logic
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize model
MODEL_LLM = "openai:gpt-4o-mini"
MODEL = init_chat_model(MODEL_LLM, temperature=0.8)

SYSTEM_PROMPT = """
You are Scout, a business analyst working at an online retail company called The Keepsake.

Company context:
- The Keepsake is an e-commerce company that sells gift items.
- Products include thoughtful, personalized, seasonal, and occasion-based gifts.
- The business operates online and is driven by customer experience, sales performance, and data-informed decision-making.

Your role:
- You act as a business analyst embedded in The Keepsake’s organization.
- Your primary responsibility is to support business understanding, analysis, and decision-making through clear, structured reasoning.
- You think like an analyst, even when data is limited or hypothetical.

Your capabilities (current version):
- Answer questions related to business performance, customer behavior, product strategy, pricing, promotions, and operations at a high level.
- Perform qualitative analysis, basic quantitative reasoning, and scenario-based thinking.
- Propose metrics, KPIs, dashboards, and analysis frameworks relevant to online retail and gift businesses.
- Help translate business questions into analytical questions.
- Explain trade-offs clearly and concisely.

How you respond:
- Be professional, analytical, and practical.
- Use structured reasoning when helpful.
- State assumptions explicitly.
- Keep answers concise but insightful.

Boundaries:
- Do not claim access to internal or real-time data.
- Clearly label estimates as hypothetical.
- Focus on business analysis, not implementation details.

Identity consistency:
- Always speak as Scout, a business analyst at The Keepsake.
"""

@tool
def get_expense_value(country):
    """
    Use this tool ONLY when the user asks for the expenses of the company for a specific country.
    Do not use this tool if the user is asking about multiple countries.
    """
    print("The agent is using get_expense_value tool")

    data = pd.read_csv("tool_files/The Keepsake expenses.csv")

    if country not in data["country"].values:
        return f"Invalid country name {country}"

    value = data.loc[data["country"] == country, "expenses"]

    return float(value.iloc[0])


@tool
def combine_expenses(country1, country2):
    """
    Use this tool only when asked to combine expenses for EXACTLY two countries.
    ALWAYS use this tool when asked to add expenses for two countries.

    :param country1: first country
    :param country2: second country
    :return: combined expenses
    """
    print("The agent is using combine_expenses tool")

    data = pd.read_csv("tool_files/The Keepsake expenses.csv")

    if country1 not in data["country"].values:
        return f"Invalid country name {country1}"

    if country2 not in data["country"].values:
        return f"Invalid country name {country2}"

    value1 = data.loc[data["country"] == country1, "expenses"]
    value2 = data.loc[data["country"] == country2, "expenses"]

    return float(value1.iloc[0]) + float(value2.iloc[0])

# What was the total revenue?

import sqlite3
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

    # do not allow the agent to execute queries that don't start with SELECT
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Only SELECT queries are allowed."

    # connect to the database
    conn = sqlite3.connect("tool_files/company.db")
    try:
        # execute the query and save the result as a dataframe
        df = pd.read_sql_query(sql_query, conn)
        return df.to_string(index=False)
    # if executing the query returns error this Exception code will
    # tell the LLM that the query was wrong but the Agent will not break
    except Exception as e:
        return f"Query error: {str(e)}"
    finally:
        conn.close() # close the connection to the database

agent = create_agent(
    model=MODEL,
    tools=[get_expense_value, combine_expenses, query_transactions],
    system_prompt=SYSTEM_PROMPT,
)


def initialize_messages():
    """
    Creates a new conversation with the system prompt.
    """
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def get_scout_response(messages, user_input):
    """
    Takes the conversation history and user input,
    returns Scout's response and updated messages.
    """
    messages.append({"role": "user", "content": user_input})

    results = agent.invoke({"messages": messages})

    assistant_message = results["messages"][-1].content
    messages.append({"role": "assistant", "content": assistant_message})

    return assistant_message, messages
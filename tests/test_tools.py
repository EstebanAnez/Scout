"""Tests for Scout's data tools. These run without an OpenAI key."""
import pytest

from Scout_tools import (
    calculate_profit,
    combine_expenses,
    get_expense_value,
    query_transactions,
)


def test_expense_lookup_returns_number_for_known_country():
    assert get_expense_value.invoke({"country": "France"}) == 6000.0


def test_expense_lookup_rejects_unknown_country():
    assert "Invalid country name" in get_expense_value.invoke({"country": "Atlantis"})


def test_combine_expenses_adds_two_countries():
    total = combine_expenses.invoke({"country1": "United Kingdom", "country2": "France"})
    assert total == 5000.0 + 6000.0


def test_combine_expenses_rejects_unknown_country():
    result = combine_expenses.invoke({"country1": "France", "country2": "Atlantis"})
    assert "Invalid country name" in result


@pytest.mark.parametrize(
    "revenue, expenses, profit",
    [(100.0, 40.0, 60.0), (0.0, 25.5, -25.5), (1_000_000.0, 1_000_000.0, 0.0)],
)
def test_profit_is_revenue_minus_expenses(revenue, expenses, profit):
    assert calculate_profit.invoke({"revenue": revenue, "expenses": expenses}) == profit


def test_sql_tool_answers_select_queries():
    result = query_transactions.invoke(
        {"sql_query": "SELECT COUNT(*) AS n FROM raw_transactions"}
    )
    assert "541909" in result


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM raw_transactions",
        "DROP TABLE raw_transactions",
        "UPDATE raw_transactions SET Quantity = 0",
    ],
)
def test_sql_tool_blocks_write_queries(query):
    assert query_transactions.invoke({"sql_query": query}) == "Only SELECT queries are allowed."


def test_database_is_opened_read_only():
    # even a statement that slips past the SELECT check cannot write
    result = query_transactions.invoke(
        {"sql_query": "SELECT 1; DELETE FROM raw_transactions"}
    )
    assert "541909" in query_transactions.invoke(
        {"sql_query": "SELECT COUNT(*) AS n FROM raw_transactions"}
    )
    assert "Query error" in result

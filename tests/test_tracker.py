import pytest  
from unittest.mock import patch

from expense_tracker.reports import filter_expenses
from expense_tracker.actions import add_expense, delete_expense


@pytest.fixture
def sample_expenses():
    return {
        1: {"Amount": 100.0, "Category": "Food", "Description": "Pizza", "Date": "2026-10-01"},
        2: {"Amount": 50.0, "Category": "Transport", "Description": "Bus ticket", "Date": "2026-10-15"},
        3: {"Amount": 200.0, "Category": "Food", "Description": "Groceries", "Date": "2026-11-05"}
    }


def test_filter_by_category(sample_expenses):
    results = filter_expenses(sample_expenses, category="Food")
    assert len(results) == 2
    assert 1 in results
    assert 3 in results
    assert 2 not in results

def test_filter_by_date_range(sample_expenses):
    # Should only pick up the October expense
    results = filter_expenses(sample_expenses, start_date="2026-10-01", end_date="2026-10-31")
    assert len(results) == 2
    assert 2 in results
    assert 3 not in results

def test_filter_by_keyword(sample_expenses):
    results = filter_expenses(sample_expenses, keyword="pizza")
    assert len(results) == 1
    assert 1 in results


@patch('expense_tracker.actions.save_csv')
@patch('expense_tracker.actions.log_action')
def test_add_expense(mock_log, mock_save, sample_expenses):
    add_expense(sample_expenses, 4, 25.0, "Snacks", "Chips", "2026-10-23")
    
    assert 4 in sample_expenses
    assert sample_expenses[4]["Amount"] == 25.0
    assert sample_expenses[4]["Category"] == "Snacks"
    
    mock_save.assert_called_once()
    mock_log.assert_called_once()


@patch('expense_tracker.actions.save_csv')
@patch('expense_tracker.actions.log_action')
def test_delete_expense(mock_log, mock_save, sample_expenses):
    assert 1 in sample_expenses
    
    result = delete_expense(sample_expenses, 1)
    
    assert result is True
    assert 1 not in sample_expenses
    mock_save.assert_called_once()
    mock_log.assert_called_once()

@patch('expense_tracker.actions.save_csv')
@patch('expense_tracker.actions.log_action')
def test_delete_nonexistent_expense(mock_log, mock_save, sample_expenses):
    result = delete_expense(sample_expenses, 99)
    assert result is False
    mock_save.assert_not_called()
    
    
import pytest
from unittest.mock import MagicMock
import re

import analyze
from analyze import (
    fetch_all_users,
    fetch_all_habits,
    fetch_habits_by_periodicity,
    fetch_all_streaks,
)


@pytest.fixture
def mock_cursor():
    """Fixture to create a mock cursor"""
    return MagicMock()


def test_fetch_all_users(mock_cursor):
    expected = [(1, 'alice'), (2, 'bob')]
    mock_cursor.fetchall.return_value = expected

    result = fetch_all_users(mock_cursor)

    mock_cursor.execute.assert_called_with("SELECT user_id, username FROM users")
    assert result == expected


def test_fetch_all_habits(mock_cursor):
    expected = [('alice', 'Running'), ('bob', 'Reading')]
    mock_cursor.fetchall.return_value = expected

    result = fetch_all_habits(mock_cursor)

    mock_cursor.execute.assert_called()
    assert result == expected


def test_fetch_habits_by_periodicity(mock_cursor):
    expected = [('alice', 'Running')]
    mock_cursor.fetchall.return_value = expected

    result = fetch_habits_by_periodicity(mock_cursor, 'daily')

    expected_sql = """
    SELECT u.username, h.name
    FROM habits h
    JOIN users u ON h.user_id = u.user_id
    WHERE h.periodicity = ?
    """

    # Normalize whitespaces and compare only the essential query part
    expected_sql_normalized = re.sub(r'\s+', ' ', expected_sql.strip())
    actual_sql_normalized = re.sub(r'\s+', ' ', mock_cursor.execute.call_args[0][0].strip())

    # Assert that the normalized query matches
    assert actual_sql_normalized == expected_sql_normalized

    assert result == expected


def test_fetch_all_streaks(mock_cursor):
    expected = [('alice', 'Running', 10), ('bob', 'Reading', 7)]
    mock_cursor.fetchall.return_value = expected

    result = fetch_all_streaks(mock_cursor)

    mock_cursor.execute.assert_called()
    assert result == expected


def test_fetch_streak_for_habit(mock_cursor):
    mock_cursor.fetchall.return_value = [("user1", 5)]

    result = analyze.fetch_streak_for_habit(mock_cursor, "Running")

    expected_sql = """
    SELECT u.username, s.count
    FROM habits h
    JOIN users u ON h.user_id = u.user_id
    JOIN streak s ON h.habit_id = s.habit_id
    WHERE h.name = ?
    """

    # Normalize whitespaces and compare only the essential query part
    expected_sql_normalized = re.sub(r'\s+', ' ', expected_sql.strip())
    actual_sql_normalized = re.sub(r'\s+', ' ', mock_cursor.execute.call_args[0][0].strip())

    # Assert that the normalized query matches
    assert actual_sql_normalized == expected_sql_normalized

    assert result == [("user1", 5)]


# Run the tests
if __name__ == '__main__':
    pytest.main()

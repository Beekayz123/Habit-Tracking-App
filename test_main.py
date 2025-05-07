from datetime import datetime

import pytest


# ---- Fixture: Mock DB Connection ----
@pytest.fixture
def mock_db():
    """
    Mocks the database connection and cursor using MagicMock.
    """
    with patch('main.get_connection') as mock_conn:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        mock_conn.return_value.__enter__.return_value = conn
        yield conn, cursor


# ---- Test: Successful Habit Addition ----
def test_add_habit_success(mock_db):
    """
    Test case for the 'add_habit' function in the 'main' module.
    Verifies that a habit is successfully added to the database and the commit are made.
    """
    conn, cursor = mock_db
    cursor.fetchone.return_value = None  # No existing habit with the same name

    with patch('main.questionary.text') as mock_text, \
            patch('main.questionary.select') as mock_select, \
            patch('main.questionary.print') as mock_print:
        # Mock user inputs
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Exercise")),  # Habit name
            MagicMock(ask=MagicMock(return_value="Daily jogging"))  # Description
        ]
        mock_select.return_value.ask.return_value = "daily"  # Frequency

        main.add_habit(123, "testuser")

        cursor.execute.assert_any_call(
            "SELECT 1 FROM habit WHERE user_id = ? AND name = ?",
            (123, "Exercise")
        )
        # Capture the INSERT query call
        insert_calls = [call for call in cursor.execute.call_args_list if "INSERT INTO habit" in call[0][0]]
        assert len(insert_calls) == 1
        args = insert_calls[0][0][1]
        assert args[0] == 123
        assert args[1] == "Exercise"
        assert args[2] == "Daily jogging"
        assert args[3] == "daily"
        assert isinstance(args[4], datetime)
        conn.commit.assert_called_once()
        mock_print.assert_called_once_with("✅ 'Exercise' added!")


def test_add_habit_duplicate(mock_db):
    """
    Test case for 'add_habit' when a duplicate habit name exists for the same user.
    Should print an error and not insert again.
    """
    conn, cursor = mock_db
    cursor.fetchone.return_value = (1,)  # Simulate existing habit

    with patch('main.questionary.text') as mock_text, \
            patch('main.questionary.select') as mock_select, \
            patch('main.questionary.print') as mock_print:
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Exercise")),
            MagicMock(ask=MagicMock(return_value="Daily jogging"))
        ]
        mock_select.return_value.ask.return_value = "daily"

        main.add_habit(123, "testuser")

        cursor.execute.assert_any_call(
            "SELECT 1 FROM habit WHERE user_id = ? AND name = ?",
            (123, "Exercise")
        )
        conn.commit.assert_not_called()
        mock_print.assert_called_once_with("❌ You already have that habit.")


def test_log_completion_insert(mock_db):
    """
    Test logging a habit completion where the habit exists and no prior record is in 'completion'.
    It should insert a new record and print the streak.
    """
    conn, cursor = mock_db

    # Simulate habit exists
    cursor.fetchone.side_effect = [
        (1,),  # habit exists
        None  # no previous completion
    ]

    with patch('main.questionary.text') as mock_text, \
            patch('main.questionary.print') as mock_print, \
            patch('main.list_user_habits') as mock_list:
        mock_text.return_value.ask.return_value = "10"  # user enters habit ID 10

        main.log_completion(123, "testuser")

        # Ensure we checked the habit exists
        cursor.execute.assert_any_call("SELECT 1 FROM habit WHERE habit_id = ? AND user_id = ?", (10, 123))

        # Ensure insert was called with correct parameters
        insert_call = [
            call for call in cursor.execute.call_args_list if "INSERT INTO completion" in call[0][0]
        ]
        assert len(insert_call) == 1
        args = insert_call[0][0][1]
        assert args[0] == 123
        assert args[1] == 10
        assert args[2] == 1  # initial count
        assert isinstance(args[3], datetime)

        conn.commit.assert_called_once()
        mock_print.assert_called_once_with("🔥 Logged! New streak: 1")
        mock_list.assert_called_once_with(123)


def test_log_completion_update(mock_db):
    """
    Test logging a habit completion where the habit exists and a prior record is found.
    It should update the existing completion record.
    """
    conn, cursor = mock_db

    # Simulate habit exists and completion record exists with count=3
    cursor.fetchone.side_effect = [
        (1,),  # habit exists
        (3,)  # previous count
    ]

    with patch('main.questionary.text') as mock_text, \
            patch('main.questionary.print') as mock_print, \
            patch('main.list_user_habits') as mock_list:
        mock_text.return_value.ask.return_value = "5"  # user enters habit ID 5

        main.log_completion(123, "testuser")

        cursor.execute.assert_any_call("SELECT 1 FROM habit WHERE habit_id = ? AND user_id = ?", (5, 123))

        update_call = [
            call for call in cursor.execute.call_args_list if "UPDATE completion" in call[0][0]
        ]
        assert len(update_call) == 1
        args = update_call[0][0][1]
        assert args[0] == 4  # 3 + 1 = 4
        assert isinstance(args[1], datetime)
        assert args[2] == 5
        assert args[3] == 123

        conn.commit.assert_called_once()
        mock_print.assert_called_once_with("🔥 Logged! New streak: 4")
        mock_list.assert_called_once_with(123)


def test_log_completion_invalid_id(mock_db):
    """
    Test logging completion with non-numeric habit ID input.
    Should print an error and not execute any DB operations.
    """
    with patch('main.questionary.text') as mock_text, \
            patch('main.questionary.print') as mock_print, \
            patch('main.list_user_habits') as mock_list:
        mock_text.return_value.ask.return_value = "abc"  # invalid input
        main.log_completion(123, "testuser")

        mock_print.assert_called_once_with("❌ Invalid ID format. Please enter a number.")
        mock_list.assert_called_once_with(123)


def test_log_completion_nonexistent_habit(mock_db):
    """
    Test logging completion where the entered habit ID does not exist for user.
    Should print error and not insert or update.
    """
    conn, cursor = mock_db

    # Simulate habit does not exist
    cursor.fetchone.return_value = None

    with patch('main.questionary.text') as mock_text, \
            patch('main.questionary.print') as mock_print, \
            patch('main.list_user_habits') as mock_list:
        mock_text.return_value.ask.return_value = "7"

        main.log_completion(123, "testuser")

        cursor.execute.assert_called_with("SELECT 1 FROM habit WHERE habit_id = ? AND user_id = ?", (7, 123))
        conn.commit.assert_not_called()
        mock_print.assert_called_once_with("❌ No such habit.")
        mock_list.assert_called_once_with(123)


def test_view_habits_with_monkeypatch(monkeypatch):
    """
    Test for 'view_habits' using monkeypatch to simulate the database connection.
    Verifies correct habit output printed by the function.
    """
    printed = []

    # Dummy classes to simulate DB behavior
    class DummyCursor:
        def __init__(self):
            self._data = []

        def execute(self, *_args, **_kwargs):
            self._data = [(1, "Exercise"), (2, "Reading")]

        def fetchall(self):
            return self._data

    class DummyConn:
        @staticmethod
        def cursor():
            return DummyCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    # Patch the get_connection function to return DummyConn
    monkeypatch.setattr(main, "get_connection", lambda: DummyConn())

    # Patch the questionary.print to collect printed output
    monkeypatch.setattr(main.questionary, "print", lambda x: printed.append(x))

    # Run the function
    main.view_habits(user_id=123)  # Assuming view_habits takes a user_id

    # Assertions
    assert "Your habits are:" in printed
    assert "- Exercise (ID: 1)" in printed
    assert "- Reading (ID: 2)" in printed


def test_view_profile_success():
    # Setup mock cursor and connection
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("testuser", "2024-01-01")
    mock_cursor.fetchall.return_value = [("Exercise", 10), ("Reading", 5)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Create a context manager mock for get_connection()
    mock_conn_cm = MagicMock()
    mock_conn_cm.__enter__.return_value = mock_conn
    mock_conn_cm.__exit__.return_value = None

    printed_output = []

    # Patch where it is used: main.get_connection and main.questionary.print
    with patch("main.get_connection", return_value=mock_conn_cm), \
            patch("main.questionary.print", side_effect=lambda msg: printed_output.append(msg)):
        main.view_profile(user_id=123)

    # Assert expected prints
    assert "👤 Profile for testuser:" in printed_output
    assert "   - Username: testuser" in printed_output
    assert "   - Account created on: 2024-01-01" in printed_output
    assert "🔖 Your habit completions:" in printed_output
    assert "   - Habit: Exercise | Streak: 10 completions" in printed_output
    assert "   - Habit: Reading | Streak: 5 completions" in printed_output


# Case 1: Successful deletion
def test_delete_habit_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [("Workout",)]  # habit name
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cm = MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda s, exc_type, exc_val, exc_tb: None)

    with patch("main.get_connection", return_value=mock_cm), \
            patch("main.questionary.text", return_value=MagicMock(ask=lambda: "1")), \
            patch("main.questionary.confirm", return_value=MagicMock(ask=lambda: True)), \
            patch("main.questionary.print") as mock_print, \
            patch("main.list_user_habits"):  # mock list_user_habits to avoid extra prints
        main.delete_habit(user_id=123)

    mock_conn.commit.assert_called_once()
    mock_print.assert_any_call("🗑️ Habit deleted successfully.")


# Case 2: Invalid ID entered
def test_delete_habit_invalid_id():
    with patch("main.questionary.text", return_value=MagicMock(ask=lambda: "abc")), \
            patch("main.questionary.print") as mock_print, \
            patch("main.list_user_habits"), \
            patch("main.get_connection"):  # Should not be used
        main.delete_habit(user_id=123)

    mock_print.assert_called_with("❌ Invalid ID. Please enter a number.")


# Case 3: Habit not found in DB
def test_delete_habit_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # No matching habit
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cm = MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda s, exc_type, exc_val, exc_tb: None)

    with patch("main.get_connection", return_value=mock_cm), \
            patch("main.questionary.text", return_value=MagicMock(ask=lambda: "1")), \
            patch("main.questionary.print") as mock_print, \
            patch("main.list_user_habits"):
        main.delete_habit(user_id=123)

    mock_print.assert_called_with("❌ No such habit found.")


# Case 4: Deletion cancelled by user
def test_delete_habit_cancelled():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("Workout",)  # Habit exists
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cm = MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda s, exc_type, exc_val, exc_tb: None)

    with patch("main.get_connection", return_value=mock_cm), \
            patch("main.questionary.text", return_value=MagicMock(ask=lambda: "1")), \
            patch("main.questionary.confirm", return_value=MagicMock(ask=lambda: False)), \
            patch("main.questionary.print") as mock_print, \
            patch("main.list_user_habits"):
        main.delete_habit(user_id=123)

    mock_print.assert_called_with("❎ Deletion canceled.")

def test_log_in_success():
    with patch("main.questionary.text", return_value=MagicMock(ask=lambda: "testuser")), \
         patch("main.questionary.password", return_value=MagicMock(ask=lambda: "testpass")), \
         patch("main.get_connection") as mock_conn_fn, \
         patch("main.questionary.print") as mock_print:

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # user_id
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_fn.return_value.__enter__.return_value = mock_conn

        user_id, username = main.log_in()

    assert user_id == 1
    assert username == "testuser"
    mock_print.assert_called_with("👋 Welcome back, testuser!")

def test_log_in_invalid_credentials():
    with patch("main.questionary.text", return_value=MagicMock(ask=lambda: "wronguser")), \
         patch("main.questionary.password", return_value=MagicMock(ask=lambda: "wrongpass")), \
         patch("main.get_connection") as mock_conn_fn, \
         patch("main.questionary.print") as mock_print:

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_fn.return_value.__enter__.return_value = mock_conn

        user_id, username = main.log_in()

    assert user_id is None
    assert username is None
    mock_print.assert_called_with("❌ Invalid credentials.")

from unittest.mock import patch, MagicMock
import main


def test_view_analytics():
    printed_output = []

    with patch("main.get_connection") as mock_conn_fn, \
         patch("main.questionary.print", side_effect=lambda msg: printed_output.append(msg)):

        # Set up mock cursor with sequential fetchone() return values
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            (3,),       # total_habits
            (12,),      # total_completions
            (2,)        # today_completions
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_fn.return_value.__enter__.return_value = mock_conn

        main.view_analytics(user_id=123)

    # Assertions
    assert f"📊 Analytics for today:" in printed_output
    assert f"• Total habits: 3" in printed_output
    assert f"• Total completions: 12" in printed_output
    assert f"• Completions today: 2" in printed_output

def test_list_user_habits_with_data():
    printed_output = []

    with patch("main.get_connection") as mock_conn_fn, \
         patch("main.questionary.print", side_effect=lambda msg: printed_output.append(msg)):

        # Simulate habit records
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "Exercise"), (2, "Read Book")]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_fn.return_value.__enter__.return_value = mock_conn

        main.list_user_habits(user_id=123)

    assert "🔍 [Debug] Your habits right now:" in printed_output
    assert "   • ID 1 → Exercise" in printed_output
    assert "   • ID 2 → Read Book" in printed_output


def test_list_user_habits_empty():
    printed_output = []

    with patch("main.get_connection") as mock_conn_fn, \
         patch("main.questionary.print", side_effect=lambda msg: printed_output.append(msg)):

        # Simulate no habits
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_fn.return_value.__enter__.return_value = mock_conn

        main.list_user_habits(user_id=123)

    assert "⚠️ [Debug] You have no habits in the DB." in printed_output


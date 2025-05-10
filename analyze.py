from typing import List, Tuple
import sqlite3
from functools import reduce
import questionary
from db import create_connection as get_connection

# ---------------------------
# Helper functions (functional style)
# ---------------------------

def fetch_all_users(cursor) -> List[Tuple[int, str]]:
    cursor.execute("SELECT user_id, username FROM user_info")
    return cursor.fetchall()


def fetch_all_habits(cursor) -> List[Tuple[str, str]]:
    cursor.execute("""
        SELECT u.username, h.name
        FROM habit h
        JOIN user_info u ON h.user_id = u.user_id
    """)
    return cursor.fetchall()


def fetch_habits_by_periodicity(cursor, periodicity: str) -> List[Tuple[str, str]]:
    try:
        cursor.execute("""
            SELECT u.username, h.name
            FROM habit h
            JOIN user_info u ON h.user_id = u.user_id
            WHERE h.periodicity = ?
        """, (periodicity,))
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        questionary.print(f"⚠️ Cannot filter by periodicity: Error: {e}")
        return []


def fetch_all_completions(cursor) -> List[Tuple[str, str, int]]:
    cursor.execute("""
        SELECT u.username, h.name, c.count
        FROM habit h
        JOIN user_info u ON h.user_id = u.user_id
        JOIN completion c ON h.habit_id = c.habit_id
    """)
    return cursor.fetchall()


def fetch_completions_for_habit(cursor, habit_name: str) -> List[Tuple[str, int]]:
    cursor.execute("""
        SELECT u.username, c.count
        FROM habit h
        JOIN user_info u ON h.user_id = u.user_id
        JOIN completion c ON h.habit_id = c.habit_id
        WHERE h.name = ?
    """, (habit_name,))
    return cursor.fetchall()

# ---------------------------
# Analytics Interface
# ---------------------------

def run_analytics():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            while True:
                choice = questionary.select(
                    "📊 Analytics Menu - Choose an analysis option:",
                    choices=[
                        "List all currently tracked habits (all users)",
                        "List habits by periodicity (all users)",
                        "Longest streak across all habits (all users)",
                        "Longest streak for a specific habit (all users)",
                        "Back to Main Menu"
                    ]
                ).ask()

                if choice == "List all currently tracked habits (all users)":
                    habits = fetch_all_habits(cursor)
                    if habits:
                        questionary.print("📋 Tracked Habits (by user):")
                        for user, habit in habits:
                            questionary.print(f"- {user}: {habit}")
                    else:
                        questionary.print("⚠️ No habits found.")

                elif choice == "List habits by periodicity (all users)":
                    period = questionary.select("Select periodicity:", choices=["daily", "weekly"]).ask()
                    habits = fetch_habits_by_periodicity(cursor, period)
                    if habits:
                        questionary.print(f"📅 {period.capitalize()} Habits (by user):")
                        for user, habit in habits:
                            questionary.print(f"- {user}: {habit}")
                    else:
                        questionary.print(f"⚠️ No {period} habits found.")

                elif choice == "Longest streak across all habits (all users)":
                    completions = fetch_all_completions(cursor)
                    if completions:
                        longest = reduce(lambda a, b: a if a[2] > b[2] else b, completions)
                        questionary.print(f"🏆 Longest Streak: {longest[1]} by {longest[0]} with {longest[2]} completions")
                    else:
                        questionary.print("⚠️ No completion data available.")

                elif choice == "Longest streak for a specific habit (all users)":
                    habit_name = questionary.text("Enter the habit name:").ask()
                    completions = fetch_completions_for_habit(cursor, habit_name)
                    if completions:
                        for user, count in completions:
                            questionary.print(f"🔥 '{habit_name}' by {user} has a streak of {count} completions.")
                    else:
                        questionary.print(f"⚠️ No streaks found for '{habit_name}'.")

                elif choice == "Back to Main Menu":
                    break
    except Exception as e:
        questionary.print(f"⚠️ An error occurred while connecting to the database: {e}")


if __name__ == '__main__':
    run_analytics()

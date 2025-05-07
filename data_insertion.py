import sqlite3
from datetime import datetime

def create_connection():
    """Create a database connection and return the connection object."""
    conn = sqlite3.connect('habit_tracker.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def insert_habit_completions():
    """
    For the default_user, delete any old completions and
    insert one new completion per habit with specific counts.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Get default_user id
    cursor.execute('SELECT user_id FROM user_info WHERE username = ?', ('default_user',))
    user = cursor.fetchone()
    if not user:
        print("❌ default_user not found. Make sure you inserted it first.")
        return

    user_id = user[0]

    # Delete existing completions
    cursor.execute('DELETE FROM completion WHERE user_id = ?', (user_id,))

    # Fetch all habit_ids, ordered
    cursor.execute('SELECT habit_id FROM habit WHERE user_id = ? ORDER BY habit_id', (user_id,))
    habit_ids = [row[0] for row in cursor.fetchall()]

    # Define the exact counts for each habit
    counts = [20, 21, 4, 5, 4]  # habit 1 ➔ 20, habit 2 ➔ 21, habits 3-5 ➔ 4,5,4

    if len(habit_ids) != len(counts):
        print("❌ Mismatch between habits and counts! Please adjust your counts list.")
        return

    now = datetime.now()

    # Insert completions
    for hid, cnt in zip(habit_ids, counts):
        cursor.execute('''
            INSERT INTO completion (user_id, habit_id, last_completed, count)
            VALUES (?, ?, ?, ?)
        ''', (user_id, hid, now, cnt))

    conn.commit()
    conn.close()
    print("✅ Completions inserted with the specific counts: 20, 21, 4, 5, 4.")

if __name__ == '__main__':
    insert_habit_completions()

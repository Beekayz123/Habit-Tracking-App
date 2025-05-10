import sqlite3
import questionary
from db import create_connection as get_connection

# ---------------------------
# Create a new account
# ---------------------------
def create_account():
    username = questionary.text("Choose your desired username:").ask()
    password = questionary.password("Enter your password:").ask()

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_info (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Catches the UNIQUE constraint on username
            questionary.print(f"❌ The username '{username}' is already taken. Please choose another.")
            return

    questionary.print(f"✅ Account '{username}' created successfully!")

def log_in():
    username = questionary.text("Username:").ask()
    password = questionary.password("Password:").ask()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM user_info WHERE username = ? AND password = ?",
                  (username, password))
        row = c.fetchone()
    if row:
        questionary.print(f"👋 Welcome back, {username}!")
        return row[0], username
    else:
        questionary.print("❌ Invalid credentials.")
        return None, None

# Habit-management actions (now take current_user_id as first arg)
def add_habit(user_id, _username):
    name = questionary.text("Enter the habit name:").ask()
    desc = questionary.text("Enter a description (optional):").ask()
    period = questionary.select("Frequency:", choices=["daily", "weekly"]).ask()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM habit WHERE user_id = ? AND name = ?", (user_id, name))
        if c.fetchone():
            return questionary.print("❌ You already have that habit.")
        c.execute(
            "INSERT INTO habit (user_id, name, description, periodicity, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, desc, period, datetime.now())
        )
        conn.commit()
    questionary.print(f"✅ '{name}' added!")


def view_habits(user_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT habit_id, name FROM habit WHERE user_id = ?", (user_id,))
            habits = c.fetchall()

            if not habits:
                return questionary.print("❌ No habits found.")

            questionary.print("Your habits are:")
            for habit in habits:
                questionary.print(f"- {habit[1]} (ID: {habit[0]})")
    except Exception as e:
        questionary.print(f"❌ Error: {str(e)}")


def list_user_habits(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT habit_id, name FROM habit WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
    if not rows:
        questionary.print("⚠️ [Debug] You have no habits in the DB.")
    else:
        questionary.print("🔍 [Debug] Your habits right now:")
        for hid, name in rows:
            questionary.print(f"   • ID {hid} → {name}")


def log_completion(user_id, _username):
    # 👇 Add this line to show all current habits before asking for Habit ID
    list_user_habits(user_id)

    hid = questionary.text("Habit ID you completed:").ask()
    try:
        hid = int(hid)
    except ValueError:
        return questionary.print("❌ Invalid ID format. Please enter a number.")

    # Debugging: Print the habit_id and user_id values before checking the habit in the database
    print(f"Checking habit_id={hid}, user_id={user_id}")

    now = datetime.now()
    with get_connection() as conn:
        c = conn.cursor()
        # Check if habit exists for the given user_id and habit_id
        c.execute("SELECT 1 FROM habit WHERE habit_id = ? AND user_id = ?", (hid, user_id))
        if not c.fetchone():
            return questionary.print("❌ No such habit.")

        # upsert into completion
        c.execute("SELECT count FROM completion WHERE habit_id = ? AND user_id = ?", (hid, user_id))
        row = c.fetchone()
        if row:
            nc = row[0] + 1
            c.execute("UPDATE completion SET count = ?, last_completed = ? WHERE habit_id = ? AND user_id = ?",
                      (nc, now, hid, user_id))
        else:
            nc = 1
            c.execute(
                "INSERT INTO completion (user_id, habit_id, count, last_completed) VALUES (?, ?, ?, ?)",
                (user_id, hid, nc, now)
            )
        conn.commit()

    questionary.print(f"🔥 Logged! New streak: {nc}")

# Other functions like get_connection, list_user_habits...

def delete_habit(user_id):
    list_user_habits(user_id)

    hid = questionary.text("Enter the ID of the habit you want to delete:").ask()

    try:
        hid = int(hid)
    except ValueError:
        questionary.print("❌ Invalid ID. Please enter a number.")
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM habit WHERE habit_id = ? AND user_id = ?", (hid, user_id))
        row = c.fetchone()
        if not row:
            questionary.print("❌ No such habit found.")
            return

        confirm = questionary.confirm(f"Are you sure you want to delete habit '{row[0]}'?").ask()
        if not confirm:
            questionary.print("❎ Deletion canceled.")
            return

        c.execute("DELETE FROM habit WHERE habit_id = ? AND user_id = ?", (hid, user_id))
        conn.commit()

    questionary.print("🗑️ Habit deleted successfully.")

def view_profile(user_id):
    with get_connection() as conn:
        c = conn.cursor()

        # Fetch user info (username and account creation date)
        c.execute("SELECT username, created_at FROM user_info WHERE user_id = ?", (user_id,))
        user = c.fetchone()

        if user:
            username, created_at = user
            questionary.print(f"👤 Profile for {username}:")
            questionary.print(f"   - Username: {username}")
            questionary.print(f"   - Account created on: {created_at}")

            # Fetch habit completion data for the user
            c.execute("""
                SELECT h.name, c.count
                FROM habit h
                JOIN completion c ON h.habit_id = c.habit_id
                WHERE h.user_id = ?
            """, (user_id,))
            habits = c.fetchall()

            if habits:
                questionary.print("🔖 Your habit completions:")
                for habit_name, count in habits:
                    questionary.print(f"   - Habit: {habit_name} | Streak: {count} completions")
            else:
                questionary.print("❌ No habits completed yet.")
        else:
            questionary.print("❌ Profile not found.")


def delete_account(user_id):
    with get_connection() as conn:
        c = conn.cursor()

        # Check if the user exists in the user_info table
        c.execute("SELECT username FROM user_info WHERE user_id = ?", (user_id,))
        user = c.fetchone()

        if not user:
            questionary.print("❌ No such account found.")
            return

        username = user[0]

        # Ask for confirmation to delete the account
        confirm = questionary.confirm(
            f"Are you sure you want to delete your account, '{username}'? This action cannot be undone.").ask()

        if not confirm:
            questionary.print("❎ Account deletion canceled.")
            return

        # Delete the user's habits and completions first to avoid foreign key constraint errors
        c.execute("DELETE FROM completion WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM habit WHERE user_id = ?", (user_id,))

        # Now, delete the user from the user_info table
        c.execute("DELETE FROM user_info WHERE user_id = ?", (user_id,))
        conn.commit()

    questionary.print(f"🗑️ Account '{username}' deleted successfully.")

from datetime import datetime, date

def view_analytics(user_id):
    today = date.today()  # Gets today's date in yyyy-mm-dd format
    with get_connection() as conn:
        c = conn.cursor()

        # Total habits
        c.execute("SELECT COUNT(*) FROM habit WHERE user_id = ?", (user_id,))
        total_habits = c.fetchone()[0]

        # Total completions
        c.execute("SELECT SUM(count) FROM completion WHERE user_id = ?", (user_id,))
        total_completions = c.fetchone()[0] or 0

        # Completions today
        c.execute("SELECT COUNT(*) FROM completion WHERE user_id = ? AND DATE(last_completed) = ?", (user_id, today))
        today_completions = c.fetchone()[0]

    questionary.print(f"📊 Analytics for today:")
    questionary.print(f"• Total habits: {total_habits}")
    questionary.print(f"• Total completions: {total_completions}")
    questionary.print(f"• Completions today: {today_completions}")

def user_menu(user_id, username):
    while True:
        choice = questionary.select(
            f"👤 Welcome {username}! What would you like to do?",
            choices=[
                "Add a Habit",
                "View Habits",
                "Log Habit Completion",
                "Delete a Habit",
                "View Profile",
                "View Analytics",
                "Delete Account",
                "Log Out"
            ]
        ).ask()

        if choice == "Add a Habit":
            add_habit(user_id, username)

        elif choice == "View Habits":
            view_habits(user_id)

        elif choice == "Log Habit Completion":
            log_completion(user_id, username)

        elif choice == "Delete a Habit":
            delete_habit(user_id)

        elif choice == "View Profile":
            view_profile(user_id)

        elif choice == "View Analytics":
            view_analytics(user_id)

        elif choice == "Delete Account":
            delete_account(user_id)

        elif choice == "Log Out":
            print("🔒 Logging out...")
            break

# —————————————————————————————
# Top-level menu
# —————————————————————————————
def main():
    while True:
        choice = questionary.select(
            "🏠 Main Menu",
            choices=["Create an Account", "Log In", "Exit"]
        ).ask()

        if choice == "Create an Account":
            create_account()
        elif choice == "Log In":
            uid, uname = log_in()
            if uid:
                user_menu(uid, uname)
        else:  # Exit
            break

if __name__ == "__main__":
    main()


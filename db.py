import sqlite3

def create_connection():
    """Create a database connection and return the connection object."""
    conn = sqlite3.connect('habit_tracker.db')
    conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key constraint
    return conn

def create_tables():
    """Create user_info, habit, and completion tables with proper relationships."""
    conn = create_connection()
    cursor = conn.cursor()

    # Create user_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,  
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create habit table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            periodicity TEXT CHECK(periodicity IN ('daily', 'weekly')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_info(user_id) ON DELETE CASCADE
        )
    ''')

    # Create completion table (one row per habit)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completion (
            completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_id INTEGER NOT NULL,
            last_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id)   REFERENCES user_info(user_id) ON DELETE CASCADE,
            FOREIGN KEY (habit_id)  REFERENCES habit(habit_id)   ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def insert_predefined_habits():
    """Insert 5 predefined habits into the habit table for a default user."""
    conn = create_connection()
    cursor = conn.cursor()

    # 1) ensure default user
    cursor.execute('''
        INSERT OR IGNORE INTO user_info (username, password, email)
        VALUES (?, ?, ?)
    ''', ('default_user', 'password123', 'default@example.com'))

    # 2) fetch its ID
    cursor.execute('SELECT user_id FROM user_info WHERE username = ?', ('default_user',))
    user_id = cursor.fetchone()[0]

    # 3) your five habits
    habits = [
        ('Drink Water',      'Drink at least 8 glasses of water', 'daily'),
        ('Morning Jog',      'Go for a 30-minute jog every morning', 'daily'),
        ('Read a Book',      'Read at least 50 pages of a book',  'weekly'),
        ('Clean House',      'Deep clean the house',              'weekly'),
        ('Plan Weekly Goals','Plan goals every Sunday evening',   'weekly'),
    ]

    for name, desc, period in habits:
        cursor.execute('''
            INSERT OR IGNORE INTO habit (user_id, name, description, periodicity)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, desc, period))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    insert_predefined_habits()
    print("✅ Database and tables created successfully with predefined habits.")


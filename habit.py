# habit.py

class UserInfo:
    """
    A class to represent a user in the habit tracker system.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
        email (str, optional): The email address of the user.
        user_id (int, optional): The unique ID of the user (assigned by the database).
    """

    def __init__(self, username, password, email=None):
        self.username = username
        self.password = password
        self.email = email
        self.user_id = None  # To be set after inserting into database


class Habit:
    """
    A class to represent a habit created by a user.

    Attributes:
        user_id (int): The ID of the user who created the habit.
        name (str): The name of the habit.
        description (str): A short description of the habit.
        periodicity (str): How often the habit should be done ('daily' or 'weekly').
        habit_id (int, optional): The unique ID of the habit (assigned by the database).
    """

    def __init__(self, user_id, name, description, periodicity):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.periodicity = periodicity  # Must be 'daily' or 'weekly'
        self.habit_id = None  # To be set after inserting into database

class Completion:
    """
    A class to represent the completion record of a habit by a user.

    Attributes:
        user_id (int): The ID of the user who completed the habit.
        habit_id (int): The ID of the habit that was completed.
        last_completed (str, optional): The date and time when the habit was last completed (default to current timestamp in database).
        count (int, optional): The number of times the habit has been completed (defaults to 1).
        completion_id (int, optional): The unique ID of the completion record (assigned by the database).
    """

    def __init__(self, user_id, habit_id, last_completed=None, count=1):
        self.user_id = user_id
        self.habit_id = habit_id
        self.last_completed = last_completed  # This now corresponds to the 'last_completed' field in the database
        self.count = count  # New attribute to match database
        self.completion_id = None  # To be set after inserting into database

# Habit Tracking App

Habit Tracker is a Python-based command-line interface (CLI) application that helps users create, manage, track, and analyze their habits. It offers a simple interface for handling daily and weekly tasks, maintaining streaks, and analyzing progress over time.

## Table of Contents

- [Features](#features)
  - [User Management](#user-management)
  - [Habit Management](#habit-management)
  - [Analytics](#analytics)
  - [Interface](#interface)
- [Technical Requirements](#technical-requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Main Menu Commands](#main-menu-commands)
  - [In-App Commands](#in-app-commands)
  - [Analytics Commands](#analytics-commands)
  - [Test Data Generation](#test-data-generation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)

---

## Features

### User Management

- Secure login and registration system for user authentication.
- Personalized user profiles with saved data.
- Starter templates to help users begin tracking habits immediately.

### Habit Management

- Add, update, or delete habits.
- Track completion for daily and weekly routines.
- Edit habit descriptions to suit your needs.
- Maintain habit streaks to boost motivation.

### Analytics

- Display all tracked habits.
- Filter by daily or weekly tracking.
- View the longest streak across all habits or a specific one.
- Understand completion trends with habit analytics.

### Interface

- Clean and intuitive CLI layout.
- Interactive, menu-driven command navigation.
- Real-time user prompts and feedback.

---

## Technical Requirements

- Python 3.7 or later  
- SQLite3 (Standard Library)  
- `questionary`  
- `pytest`  
- Virtual environment (recommended)

---

## Installation

To set up the project locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Beekayz123/Habit-Tracking-App.git

Navigate into the project directory:
cd habit-tracker
Create and activate a virtual environment:

Windows:

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate
macOS/Linux:

bash
Copy
Edit
python -m venv
source venv/bin/activate
Install all required dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Initialize the database:

bash
Copy
Edit
python db.py
(Optional) Insert sample test data:

bash
Copy
Edit
python test_data_insertion.py
Run the application:

bash
Copy
Edit
python main.py
Usage
After launching the app, users can register or log in to begin tracking habits.

Main Menu Commands
Create Account

Login

Exit

In-App Commands (after login)
Add a Habit

View Habits

Log Habit Completion

Delete a Habit

View Profile

View Analytics

Delete Account

Log Out

Analytics Commands
1 — View all tracked habits

2 — Filter habits by daily or weekly frequency

3 — Longest streak across all habits

4 — Longest streak for a specific habit

Back — Return to the main menu

Test Data Generation
To populate the database with sample user data, run:

bash
Copy
Edit
python test_data_insertion.py
Testing
The app uses pytest to verify functionality.

Make sure to initialize the database (db.py) before running tests:

bash
Copy
Edit
pytest
Project Structure
css
Copy
Edit
habit-tracker/
├── analyze.py
├── db.py
├── habit.py
├── habit_tracker.db
├── main.py
├── test_analyze.py
├── test_main.py
├── README.md
└── requirements.txt
Dependencies
These libraries are required:

questionary

pytest

sqlite3 (Python Standard Library)

os (Python Standard Library)

datetime (Python Standard Library)

Install all dependencies with:

bash
Copy
Edit
pip install -r requirements.txt
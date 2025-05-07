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

# Habit Tracker CLI App

## Setup Instructions

### 2. Create and activate a virtual environment

#### For Windows:
1. Open your terminal (e.g., Command Prompt or PowerShell).
2. Navigate to the project directory.
3. Run the following command to create a virtual environment:
   ```bash
   python -m venv venv
Activate the virtual environment:
venv\Scripts\activate
#### For macOS/Linux:
Open your terminal.

Navigate to the project directory.

Run the following command to create a virtual environment:
python -m venv 
Activate the virtual environment:
source venv/bin/activate

### 3.  Install all required dependencies
Run the following command to install the dependencies:
pip install -r requirements.txt

### 4. Initialize the database
python db.py

### 5. (Optional) Insert sample test data
python test_data_insertion.py

### 6. Run the application
python main.py
### Usage
After launching the app, users can register or log in to begin tracking habits.

### Main Menu Commands
Create Account

Login

Exit

### In-App Commands (after login)
Add a Habit

View Habits

Log Habit Completion

Delete a Habit

View Profile

View Analytics

Delete Account

Log Out

### Analytics Commands
View all tracked habits

Filter habits by daily or weekly frequency

Longest streak across all habits

Longest streak for a specific habit

Back — Return to the main menu

### Test Data Generation
To populate the database with sample user data, run:
python test_data_insertion.py

### Testing
The app uses pytest to verify functionality.
Make sure to initialize the database (db.py) before running tests:
pytest

### Project Structure
habit-tracker/
├── analyze.py
├── db.py
├── habit.py
├── habit_tracker.db
├── main.py
├── test_analyze.py
├── test_main.py
├── test_data_insertion.py    
├── .gitignore                
├── README.md
└── requirements.txt

### Dependencies
questionary

pytest

sqlite3 (Standard Library)

os (Standard Library)

datetime (Standard Library)

Install all dependencies with:
pip install -r requirements.txt

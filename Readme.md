## Games Information Query (IQ) Database

### Introduction

This project manages a comprehensive dataset of video game information, spanning **multiple eras and platforms**—from the latest game releases to classic joystick consoles.

Through a user-friendly interface, users can:

* Explore **details about games**, including ratings, genres, and sales.
* Learn about **producers, developers, and publishers**.
* View their **friends' gaming activities**.
* **Insert new records** into the database, such as games, players, or associated publishers and developers.

---

### How to Run

```bash
pip install -r requirements.txt
python UI.py
```

---

### System Structure

Our project is a **GUI-based database interaction system** built with **PySide6**. It consists of four main components:

#### 1. `data/` folder

* Contains all the **CSV datasets**.
* These datasets are automatically loaded and inserted into the database during initialization.

#### 2. `UI.py` – User Interface

Implements the full graphical interface with three primary windows:

* **Login Window**: Users connect to their MySQL database.
* **Main Menu**: Allows navigation between query and insertion modules.
* **Query/Insert Interface**: Enables users to run predefined queries or insert new data records.

#### 3. `initialize.py` – Database Setup

* Initializes the MySQL database and its tables (if they do not already exist).
* Loads data from the `data/` folder and inserts them in the proper relational order.

#### 4. `queries.py` – SQL Logic

* Contains all **SQL queries** written in Python functions.
* Each function receives input from the UI, executes a query on the database, and returns results to be displayed.

---

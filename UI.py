from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox, QLineEdit, QTextEdit, QMessageBox, QFormLayout, QTableWidget, QTableWidgetItem
)
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtCore import Qt
import sys
import mysql.connector
import queries
from initialize import initialize
from decimal import Decimal
from datetime import datetime

class Intro(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect to MySQL")
        self.setWindowIcon(QIcon(" icon.png"))
        self.resize(400, 250)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        # Title
        title = QLabel("Connect to MySQL")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instruction = QLabel("Please input your MySQL login info:")
        instruction.setStyleSheet("font-size: 14px;")
        layout.addWidget(instruction)

        # Username input
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        layout.addWidget(self.user_input)

        # Password input
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                border-radius: 6px;
                background-color: #3a7;
                color: white;
            }
            QPushButton:hover {
                background-color: #5c9;
            }
        """)
        self.connect_button.clicked.connect(self.try_connect)
        layout.addWidget(self.connect_button)

    def try_connect(self):
        user = self.user_input.text()
        password = self.pass_input.text()

        try:
            myConnection = mysql.connector.connect(
                user=user,
                password=password,
                host='localhost',
            )
            print("✅ MySQL connected:", myConnection)

            cursorObject = myConnection.cursor()
            initialize(cursorObject, "GameInfo")

            QMessageBox.information(self, "Success", "Connected to MySQL and database initialized successfully!")

            self.close()
            self.main_window = MainWindow(myConnection)
            self.main_window.show()

        except mysql.connector.Error as err:
            print("❌ MySQL connection failed:", err)
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to MySQL:\n{err}")

class MainWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        # store connection
        self.connection = connection

        self.setWindowTitle("Games Information Query (IQ) Databases")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(800, 500)  # Wider for breathing space

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)  # More space between widgets
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

        # Title
        title = QLabel("Games Information Query (IQ) Databases")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Our dataset stores game data from various eras and across many platforms.<br>"
            "Users can access information on everything from the newest releases to the oldest joystick consoles.<br><br>"
            "Game enthusiasts can explore details about games, producers, and their friends' activities.<br>"
            "In addition, users can insert new records into the database — including games, players, "
            "producers, and publishers tied to specific games."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("font-size: 14px; line-height: 1.5em;")
        layout.addWidget(description)
        layout.addStretch()
        

        # Buttons
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update Dataset")
        self.query_button = QPushButton("Query Information")
        for button in [self.update_button, self.query_button]:
            button.setMinimumWidth(150)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 8px;
                    background-color: #444;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #666;
                }
            """)
        button_layout.addStretch()
        button_layout.addWidget(self.update_button)
        button_layout.addSpacing(40)
        button_layout.addWidget(self.query_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.update_button.clicked.connect(self.open_update_window)
        self.query_button.clicked.connect(self.open_query_window)

    def open_update_window(self):
        self.update_window = UpdateWindow(self, self.connection)
        self.update_window.show()
        self.hide()

    def open_query_window(self):
        self.query_window = QueryWindow(self, self.connection)
        self.query_window.show()
        self.hide()

class UpdateWindow(QWidget):
    def __init__(self, main_window, connection):
        super().__init__()

        # store connection
        self.connection = connection
        self.main_window = main_window
        self.cursor = connection.cursor()

        self.setWindowTitle("Update Dataset")
        self.resize(500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Insert data into a table below:")
        layout.addWidget(label)

        self.table_selector = QComboBox()
        self.table_selector.addItems([
            "Games", "Achievement", "DLC", "Player", "Platform", "Developer", "Publisher",
            "Player_Platform_Games_Play", "Player_Unlock_Achievement", "Player_Use_Platform",
            "Player_Friends", "Platform_Support_Games", "Developer_Games", "Publisher_Games"
        ])
        self.table_selector.currentIndexChanged.connect(self.update_form_fields)
        layout.addWidget(QLabel("Choose a table to insert into:"))
        layout.addWidget(self.table_selector)

        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        self.insert_button = QPushButton("Insert Record")
        self.insert_button.clicked.connect(self.insert_record)
        layout.addWidget(self.insert_button)

        self.show_button = QPushButton("Show Last Record")
        self.show_button.clicked.connect(self.show_last_record)
        layout.addWidget(self.show_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.update_form_fields()

    def update_form_fields(self):
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.fields = {}

        self.fields_map = {
            "Games": ["Name", "Description", "ReleaseDate", "LanguageSupport", "Genre", "RequireAge", "Tags", "UnitsSold"],
            "Achievement": ["GameID", "Name", "Description"],
            "DLC": ["GameID", "Name", "ReleaseDate", "Price", "Description"],
            "Player": ["UserName", "Email", "Region", "JoinDate", "Level", "TotalPlayTime", "GamesOwned"],
            "Platform": ["PlatformName", "Manufacturer", "TotalGameNumber", "WebSite"],
            "Developer": ["DeveloperName", "Address", "FoundedYear", "Country", "Website"],
            "Publisher": ["PublisherName", "Address", "FoundedYear", "Country", "Website", "Description"],
            "Player_Platform_Games_Play": ["GameID", "PlatformID", "PlayerID", "TotalPlayingTime", "LastPlayTime", "PurchaseTime", "PurchasePrice", "Review", "Rating"],
            "Player_Unlock_Achievement": ["PlayerID", "GameID", "AchievementID", "GainTime"],
            "Player_Use_Platform": ["PlayerID", "PlatformID", "RegistrationDate", "TotalTimeSpent"],
            "Player_Friends": ["Player1ID", "Player2ID", "StartDate", "MutualTime"],
            "Platform_Support_Games": ["GameID", "PlatformID", "Price", "IssuedTime", "Rating"],
            "Developer_Games": ["GameID", "DeveloperID", "DevelopeStartYear", "DevelopeFinishYear", "DevelopeCost"],
            "Publisher_Games": ["GameID", "PublisherID", "PublishYear", "PublishCost"]
        }

        selected_table = self.table_selector.currentText()
        for field in self.fields_map[selected_table]:
            input_field = QLineEdit()
            self.form_layout.addRow(field + ":", input_field)
            self.fields[field] = input_field

    def get_next_id(self, table, id_field):
        self.cursor.execute(f"SELECT MAX({id_field}) FROM {table}")
        result = self.cursor.fetchone()
        return (result[0] or 0) + 1

    def insert_record(self):
        table = self.table_selector.currentText()
        field_values = {field: widget.text() or None for field, widget in self.fields.items()}

        auto_ids = {
            "Games": "GameID",
            "Player": "UserID",
            "Platform": "PlatformID",
            "Developer": "DeveloperID",
            "Publisher": "PublisherID",
            "Achievement": "AchievementID",
            "DLC": "DLCID"
        }

        new_id = "Composed"
        if table in auto_ids:
            new_id = self.get_next_id(table, auto_ids[table])
            field_values[auto_ids[table]] = new_id

        columns = ", ".join(f"`{k}`" for k in field_values)
        placeholders = ", ".join(["%s"] * len(field_values))
        values = tuple(field_values.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            self.status_label.setText(f"✅ Inserted into {table} successfully with ID {new_id}.")
        except Exception as e:
            self.connection.rollback()
            self.status_label.setText(f"❌ Insert failed: {str(e)}")

    def show_last_record(self):
        table = self.table_selector.currentText()
        primary_keys = {
            "Games": "GameID",
            "Player": "UserID",
            "Platform": "PlatformID",
            "Developer": "DeveloperID",
            "Publisher": "PublisherID",
            "Achievement": "AchievementID",
            "DLC": "DLCID"
        }

        try:
            if table in primary_keys:
                pk = primary_keys[table]
                self.cursor.execute(f"SELECT * FROM {table} ORDER BY {pk} DESC LIMIT 1")
            else:
                self.cursor.execute(f"SELECT * FROM {table} ORDER BY 1 DESC LIMIT 1")

            row = self.cursor.fetchone()
            if row:
                QMessageBox.information(self, "Last Inserted Record", str(row))
            else:
                QMessageBox.information(self, "Info", f"No records found in {table}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_back(self):
        self.main_window.show()
        self.close()

class QueryWindow(QWidget):
    def __init__(self, main_window, connection):
        super().__init__()

        # store connection
        self.connection = connection

        self.setWindowTitle("Query Interface")
        self.resize(400, 300)
        self.main_window = main_window

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Choose a category to query:")
        layout.addWidget(label)

        
        self.user_button = QPushButton("Users")
        self.games_button = QPushButton("Games")
        self.dev_pub_button = QPushButton("Developer / Publisher")
        self.platform_button = QPushButton("Platform")
        back_button = QPushButton("Back")

        
        layout.addWidget(self.user_button)
        layout.addWidget(self.games_button)
        layout.addWidget(self.dev_pub_button)
        layout.addWidget(self.platform_button)
        layout.addWidget(back_button)

        
        back_button.clicked.connect(self.go_back)
        self.platform_button.clicked.connect(self.open_platform_query_window)
        self.games_button.clicked.connect(self.open_game_query_window)
        self.dev_pub_button.clicked.connect(self.open_dev_pub_query_window)
        self.user_button.clicked.connect(self.open_user_query_window)

    def go_back(self):
        self.main_window.show()
        self.close()
    
    def open_platform_query_window(self):
        self.platform_query_window = PlatformQueryWindow(self, self.connection)
        self.platform_query_window.show()
        self.close()

    def open_game_query_window(self):
        self.platform_query_window = GamesQueryWindow(self, self.connection)
        self.platform_query_window.show()
        self.close()
    
    def open_dev_pub_query_window(self):
        self.platform_query_window = DevPubQueryWindow(self, self.connection)
        self.platform_query_window.show()
        self.close()

    def open_user_query_window(self):
        self.platform_query_window = UserQueryWindow(self, self.connection)
        self.platform_query_window.show()
        self.close()

class PlatformQueryWindow(QWidget):
    def __init__(self, main_window, connection):
        super().__init__()

        self.connection = connection
        self.cursor = connection.cursor()
        self.main_window = main_window

        self.setWindowTitle("Platform Queries")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Choose a platform-related query:")
        layout.addWidget(label)

        self.query_selector = QComboBox()
        self.query_selector.addItems([
            "1. Find all games exclusive to a platform",
            "2. List revenue of a platform during a year",
            "3. Number of users who spent more than X hours on a platform"
        ])
        layout.addWidget(self.query_selector)

        # Dynamic form area
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        self.input_widgets = {}
        self.update_input_fields()
        self.query_selector.currentIndexChanged.connect(self.update_input_fields)

        self.run_button = QPushButton("Run Query")
        self.run_button.clicked.connect(self.run_query)
        layout.addWidget(self.run_button)

        self.result_output = QLabel()
        self.result_output.setStyleSheet("color: red")
        self.result_output.setText("")
        layout.addWidget(self.result_output) 

        self.table_output = QTableWidget()
        layout.addWidget(self.table_output)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

    def update_input_fields(self):
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.input_widgets = {}
        idx = self.query_selector.currentIndex()

        # All use platform dropdown
        platform_combo = QComboBox()
        self.cursor.execute("SELECT DISTINCT PlatformName FROM Platform")
        platforms = [row[0] for row in self.cursor.fetchall()]
        platform_combo.addItems(platforms)
        self.input_widgets['platform'] = platform_combo
        self.form_layout.addRow("Platform:", platform_combo)

        if idx == 1:
            year_combo = QComboBox()
            self.cursor.execute("SELECT DISTINCT YEAR(IssuedTime) FROM Platform_Support_Games ORDER BY YEAR(IssuedTime) DESC")
            years = [str(row[0]) for row in self.cursor.fetchall() if row[0] is not None]
            year_combo.addItems(years)
            self.input_widgets['year'] = year_combo
            self.form_layout.addRow("Year:", year_combo)
        elif idx == 2:
            hours_edit = QLineEdit()
            hours_edit.setValidator(QIntValidator(1, 10000))
            hours_edit.setPlaceholderText("Enter number of hours")
            self.input_widgets['hours'] = hours_edit
            self.form_layout.addRow("Hours:", hours_edit)

    def go_back(self):
        self.main_window.show()
        self.close()

    def run_query(self):
        idx = self.query_selector.currentIndex()
        try:
            platform = self.input_widgets['platform'].currentText()
            self.result_output.setText("")
            self.table_output.clear()
            self.table_output.setRowCount(0)
            self.table_output.setColumnCount(0)

            if idx == 0:
                # 0. Find exclusive games on a platform
                results = queries.q_platform_exclusive_games(self.cursor, platform)
                columns = ["Exclusive Game Title"]

                if not results:
                    self.result_output.setStyleSheet("color: orange")
                    self.result_output.setText("No exclusive games found.")
                    return

                self.table_output.setColumnCount(len(columns))
                self.table_output.setHorizontalHeaderLabels(columns)
                self.table_output.setRowCount(len(results))

                for i, row in enumerate(results):
                    item = QTableWidgetItem(str(row[0]))
                    self.table_output.setItem(i, 0, item)

            elif idx == 1:
                # 1. Revenue estimation
                year = self.input_widgets['year'].currentText()
                result = queries.q_platform_revenue(self.cursor, platform, year)

                if not result or result[0] is None:
                    self.result_output.setStyleSheet("color: orange")
                    self.result_output.setText("No revenue result found.")
                    return

                columns = ["Estimated Revenue"]
                self.table_output.setColumnCount(1)
                self.table_output.setHorizontalHeaderLabels(columns)
                self.table_output.setRowCount(1)
                self.table_output.setItem(0, 0, QTableWidgetItem(str(result[0])))

            elif idx == 2:
                # 2. Number of users who played more than X hours
                hours = self.input_widgets['hours'].text()
                if not hours.isdigit():
                    self.result_output.setStyleSheet("color: red")
                    self.result_output.setText("Please enter a valid number for hours.")
                    return

                result = queries.q_platform_user(self.cursor, platform, hours)
                columns = ["Users Played > Hours"]
                self.table_output.setColumnCount(1)
                self.table_output.setHorizontalHeaderLabels(columns)
                self.table_output.setRowCount(1)
                self.table_output.setItem(0, 0, QTableWidgetItem(str(result[0] if result else 0)))

            self.table_output.resizeColumnsToContents()

        except Exception as e:
            self.result_output.setStyleSheet("color: red")
            self.result_output.setText(f"Query failed: {e}")

class GamesQueryWindow(QWidget):
    def __init__(self, main_window, connection):
        super().__init__()

        # store connection
        self.connection = connection
        self.cursor = connection.cursor()

        self.setWindowTitle("Game Queries")
        self.resize(600, 400)
        self.main_window = main_window

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Choose a game-related query:")
        layout.addWidget(label)

        self.query_selector = QComboBox()
        self.query_selector.addItems([
            "1. List top n games by rating on certain platform",
            "2. List all games of certain genre ordered by given attributes",
            "3. List all games produced by a specific publisher / developer along with their release date and genre, ordered by release date",
            "4. List all games released after certain year, along with their support system and the producers who made them",
            "5. List average ratings / total units sold of each genre, ordered by them in descending order"
        ])
        layout.addWidget(self.query_selector)

        # Dynamic form area for input fields
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        # Store references to widgets for access in run_query
        self.input_widgets = {}

        # Populate the initial input fields
        self.update_input_fields()

        # Connect selector to update form fields
        self.query_selector.currentIndexChanged.connect(self.update_input_fields)

        self.run_button = QPushButton("Run Query")
        self.run_button.clicked.connect(self.run_query)
        layout.addWidget(self.run_button)

        self.result_output = QLabel()
        self.result_output.setStyleSheet("color: red")
        self.result_output.setText("")
        layout.addWidget(self.result_output) 

        self.table_output = QTableWidget()
        layout.addWidget(self.table_output)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)
        
    
    def update_input_fields(self):
        """Dynamically update form fields based on selected query."""
        # Clear previous widgets
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.input_widgets = {}

        idx = self.query_selector.currentIndex()
        if idx == 0:
            # 1. platform (QComboBox), top_n (QLineEdit with int validator)
            platform_combo = QComboBox()
            self.cursor.execute("SELECT DISTINCT PlatformName FROM Platform")
            platforms = [row[0] for row in self.cursor.fetchall()]
            platform_combo.addItems(platforms)

            top_n_edit = QLineEdit()
            top_n_edit.setValidator(QIntValidator(1, 1000))
            top_n_edit.setPlaceholderText("Enter top n (number)")
            top_n_edit.setMinimumWidth(200)
            self.form_layout.addRow("Platform:", platform_combo)
            self.form_layout.addRow("Top N:", top_n_edit)
            self.input_widgets['platform'] = platform_combo
            self.input_widgets['top_n'] = top_n_edit
        elif idx == 1:
            # 2. genre (QComboBox), order_attri (QComboBox), order (QComboBox)
            genre_combo = QComboBox()
            self.cursor.execute("SELECT DISTINCT Genre FROM Games")
            genres = [row[0] for row in self.cursor.fetchall()]
            genre_combo.addItems(genres)
            order_attri_combo = QComboBox()
            order_attri_combo.addItems(['ReleaseDate', 'UnitsSold'])
            order_combo = QComboBox()
            order_combo.addItems(['ASC', 'DESC'])
            self.form_layout.addRow("Genre:", genre_combo)
            self.form_layout.addRow("Order Attribute:", order_attri_combo)
            self.form_layout.addRow("Order:", order_combo)
            self.input_widgets['genre'] = genre_combo
            self.input_widgets['order_attri'] = order_attri_combo
            self.input_widgets['order'] = order_combo
        elif idx == 2:
            search_by_combo = QComboBox()
            search_by_combo.addItems(['Publisher', 'Developer'])
            
            name_combo = QComboBox()

            self.form_layout.addRow("Search By:", search_by_combo)
            self.form_layout.addRow("Name:", name_combo)
            self.input_widgets['search_by'] = search_by_combo
            self.input_widgets['name'] = name_combo

            def update_name_combo():
                role = search_by_combo.currentText()
                name_combo.clear()
                try:
                    if role == 'Publisher':
                        self.cursor.execute("SELECT PublisherName FROM Publisher")
                    else:
                        self.cursor.execute("SELECT DeveloperName FROM Developer")
                    names = [row[0] for row in self.cursor.fetchall()]
                    name_combo.addItems(names)
                except Exception as e:
                    name_combo.addItem(f"Error: {e}")

            search_by_combo.currentIndexChanged.connect(update_name_combo)
            update_name_combo() 
        elif idx == 3:
            # 4. year (QLineEdit with int validator)
            year_edit = QLineEdit()
            year_edit.setValidator(QIntValidator(1970, 2100))
            year_edit.setPlaceholderText("Enter year (e.g., 2010)")
            year_edit.setMinimumWidth(200)
            self.form_layout.addRow("Year:", year_edit)
            self.input_widgets['year'] = year_edit
        elif idx == 4:
            # 5. type (QComboBox: Rating or UnitsSold)
            type_combo = QComboBox()
            type_combo.addItems(['Rating', 'UnitsSold'])
            self.form_layout.addRow("Type:", type_combo)
            self.input_widgets['type'] = type_combo

    def go_back(self):
        self.main_window.show()
        self.close()

    def run_query(self):
        idx = self.query_selector.currentIndex()
        result = None
        columns = []

        try:
            if idx == 0:
                # Top n games by rating on platform
                platform = self.input_widgets['platform'].currentText()
                top_n_text = self.input_widgets['top_n'].text()
                try:
                    top_n = int(top_n_text)
                except Exception:
                    self.result_output.setText("Please enter a valid number for Top N.")
                    return
                result = queries.q_game_rating(self.cursor, platform, top_n)
                columns = ["Game Name", "Rating"]

            elif idx == 1:
                # Games of genre ordered by attribute/order
                genre = self.input_widgets['genre'].currentText()
                order_attri = self.input_widgets['order_attri'].currentText()
                order = self.input_widgets['order'].currentText()
                result = queries.q_game_genre(self.cursor, genre, order_attri, order)
                columns = ["Game Name", "Genre", "Attribute Value"]

            elif idx == 2:
                # Games by publisher or developer
                search_by = self.input_widgets['search_by'].currentText()
                name = self.input_widgets['name'].currentText()
                publisher = name if search_by == 'Publisher' else None
                developer = name if search_by == 'Developer' else None
                result = queries.q_game_pub_dev(self.cursor, publisher=publisher, developer=developer)
                columns = ["Game Name", "Publisher/Developer"]

            elif idx == 3:
                # Games released after year
                year_text = self.input_widgets['year'].text()
                try:
                    year = int(year_text)
                except Exception:
                    self.result_output.setText("Please enter a valid year.")
                    return
                result = queries.q_game_year(self.cursor, year)
                columns = ["Game Name", "Release Year", "Platform", "Developer", "Publisher"]

            elif idx == 4:
                # Genre average rating/units sold
                type_val = self.input_widgets['type'].currentText()
                result = queries.q_genre_avg_rating(self.cursor, type=type_val)
                columns = ["Genre", f"Average {type_val}"]

            # ==== Display table ====
            if hasattr(result, "fetchall"):
                rows = result.fetchall()
            else:
                rows = result

            if not rows:
                self.result_output.setText("No results found.")
                self.table_output.clear()
                self.table_output.setRowCount(0)
                self.table_output.setColumnCount(0)
                return

            self.table_output.clear()
            self.table_output.setRowCount(len(rows))
            self.table_output.setColumnCount(len(columns))
            self.table_output.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table_output.setItem(i, j, item)

            self.table_output.resizeColumnsToContents()
            self.result_output.clear()

        except Exception as e:
            self.result_output.setText(f"An error occurred:\n{str(e)}")

class UserQueryWindow(QWidget):
    def __init__(self, main_window, connection):
        super().__init__()

        self.connection = connection
        self.cursor = connection.cursor()
        self.setWindowTitle("User Queries")
        self.resize(600, 400)
        self.main_window = main_window

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Choose a user-related query:")
        layout.addWidget(label)

        self.query_selector = QComboBox()
        self.query_selector.addItems([
            "1. Players ranked by achievements in a specific game",
            "2. Top N players by playtime of a game",
            "3. Total money spent by a player",
            "4. All purchases of a player",
            "5. List friends with mutual time above threshold"
        ])
        layout.addWidget(self.query_selector)

        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        self.input_widgets = {}

        self.update_input_fields()
        self.query_selector.currentIndexChanged.connect(self.update_input_fields)

        self.run_button = QPushButton("Run Query")
        self.run_button.clicked.connect(self.run_query)
        layout.addWidget(self.run_button)

        self.result_output = QLabel()
        self.result_output.setStyleSheet("color: red")
        self.result_output.setText("")
        layout.addWidget(self.result_output) 

        self.table_output = QTableWidget()
        layout.addWidget(self.table_output)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

    def update_input_fields(self):
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.input_widgets = {}
        idx = self.query_selector.currentIndex()

        if idx in [0, 1]:  # game_id + top_n
            game_id_edit = QLineEdit()
            game_id_edit.setValidator(QIntValidator(1, 100000))
            game_id_edit.setPlaceholderText("Enter Game ID")

            top_n_edit = QLineEdit()
            top_n_edit.setValidator(QIntValidator(1, 100))
            top_n_edit.setPlaceholderText("Enter Top N")

            self.form_layout.addRow("Game ID:", game_id_edit)
            self.form_layout.addRow("Top N:", top_n_edit)
            self.input_widgets['game_id'] = game_id_edit
            self.input_widgets['top_n'] = top_n_edit

        elif idx == 2:  # user_id only
            user_id_edit = QLineEdit()
            user_id_edit.setValidator(QIntValidator(1, 100000))
            user_id_edit.setPlaceholderText("Enter User ID")

            self.form_layout.addRow("User ID:", user_id_edit)
            self.input_widgets['user_id'] = user_id_edit

        elif idx == 3:  # user_id only, no top_n
            user_id_edit = QLineEdit()
            user_id_edit.setValidator(QIntValidator(1, 100000))
            user_id_edit.setPlaceholderText("Enter User ID")

            self.form_layout.addRow("User ID:", user_id_edit)
            self.input_widgets['user_id'] = user_id_edit
        elif idx == 4:
            user_id_edit = QLineEdit()
            user_id_edit.setValidator(QIntValidator(1, 100000))
            user_id_edit.setPlaceholderText("Enter User ID")

            mutual_time_edit = QLineEdit()
            mutual_time_edit.setValidator(QIntValidator(0, 100000))
            mutual_time_edit.setPlaceholderText("Minimum Mutual Time")

            self.form_layout.addRow("User ID:", user_id_edit)
            self.form_layout.addRow("Mutual Time ≥ :", mutual_time_edit)
            self.input_widgets['user_id'] = user_id_edit
            self.input_widgets['mutual_time'] = mutual_time_edit

    def go_back(self):
        self.main_window.show()
        self.close()

    def run_query(self):
        idx = self.query_selector.currentIndex()
        result = []
        columns = []

        try:
            if idx == 0:
                game_id = int(self.input_widgets['game_id'].text())
                top_n = int(self.input_widgets['top_n'].text())
                result = queries.q_user_achievements_by_game(self.cursor, game_id, top_n)
                columns = ["Player ID", "Achievements Unlocked"]

            elif idx == 1:
                game_id = int(self.input_widgets['game_id'].text())
                top_n = int(self.input_widgets['top_n'].text())
                result = queries.q_user_top_playtime_by_game(self.cursor, game_id, top_n)
                columns = ["Player Name", "Total Playtime (hrs)"]

            elif idx == 2:
                user_id = int(self.input_widgets['user_id'].text())
                result = queries.q_user_total_spent(self.cursor, user_id)
                columns = ["Total Spent ($)"]

            elif idx == 3:
                user_id = int(self.input_widgets['user_id'].text())
                result = queries.q_user_purchases(self.cursor, user_id)
                columns = ["Game", "Platform", "Price ($)", "Purchase Time"]

            elif idx == 4:
                user_id = int(self.input_widgets['user_id'].text())
                min_time = int(self.input_widgets['mutual_time'].text())
                result = queries.q_user_friends_by_mutualtime(self.cursor, user_id, min_time)
                columns = ["Friend ID", "Name", "Email", "Region", "Mutual Time (min)"]

            self.table_output.clear()
            self.table_output.setRowCount(0)
            self.table_output.setColumnCount(0)

            if not result:
                self.result_output.setStyleSheet("color: orange")
                self.result_output.setText("No results found.")
                return

            self.result_output.setText("")
            self.table_output.setColumnCount(len(columns))
            self.table_output.setHorizontalHeaderLabels(columns)
            self.table_output.setRowCount(len(result))

            for i, row in enumerate(result):
                for j, val in enumerate(row if isinstance(row, (list, tuple)) else [row]):
                    if isinstance(val, Decimal):
                        val = f"{float(val):.2f}"
                    elif isinstance(val, datetime):
                        val = val.strftime("%Y-%m-%d %H:%M:%S")
                    item = QTableWidgetItem(str(val))
                    self.table_output.setItem(i, j, item)

            self.table_output.resizeColumnsToContents()

        except Exception as e:
            self.result_output.setStyleSheet("color: red")
            self.result_output.setText(f"Query failed: {e}")

class DevPubQueryWindow(QWidget):
    def __init__(self, main_window, connection):
        super().__init__()
        self.connection = connection
        self.cursor = connection.cursor()
        self.main_window = main_window

        self.setWindowTitle("Developer / Publisher Queries")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Choose a developer or publisher query:")
        layout.addWidget(label)

        self.query_selector = QComboBox()
        self.query_selector.addItems([
            "1. List top N developers/publishers by revenue during a time period",
            "2. List developers/publishers by number of high-rated games",
            "3. List developers/publishers by number of platform-compatible games"
        ])
        layout.addWidget(self.query_selector)

        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        self.input_widgets = {}

        self.update_input_fields()
        self.query_selector.currentIndexChanged.connect(self.update_input_fields)

        self.run_button = QPushButton("Run Query")
        self.run_button.clicked.connect(self.run_query)
        layout.addWidget(self.run_button)

        self.result_output = QLabel()
        self.result_output.setStyleSheet("color: red")
        self.result_output.setText("")
        layout.addWidget(self.result_output) 

        self.table_output = QTableWidget()
        layout.addWidget(self.table_output)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

    def update_input_fields(self):
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.input_widgets = {}

        idx = self.query_selector.currentIndex()

        role_combo = QComboBox()
        role_combo.addItems(["Developer", "Publisher"])
        self.form_layout.addRow("Role:", role_combo)
        self.input_widgets["role"] = role_combo

        if idx == 0:
            start_year = QLineEdit()
            end_year = QLineEdit()
            top_n = QLineEdit()
            start_year.setValidator(QIntValidator(1970, 2100))
            end_year.setValidator(QIntValidator(1970, 2100))
            top_n.setValidator(QIntValidator(1, 100))
            self.form_layout.addRow("Start Year:", start_year)
            self.form_layout.addRow("End Year:", end_year)
            self.form_layout.addRow("Top N:", top_n)
            self.input_widgets["start_year"] = start_year
            self.input_widgets["end_year"] = end_year
            self.input_widgets["top_n"] = top_n

        elif idx == 1:
            rating = QLineEdit()
            rating.setValidator(QIntValidator(1, 5))
            rating.setPlaceholderText("Enter rating threshold (1-5)")
            self.form_layout.addRow("Rating Threshold:", rating)
            self.input_widgets["rating_threshold"] = rating

        elif idx == 2:
            platform_n = QLineEdit()
            platform_n.setValidator(QIntValidator(1, 20))
            platform_n.setPlaceholderText("Enter platform count threshold")
            self.form_layout.addRow("Min Platform Count:", platform_n)
            self.input_widgets["platform_threshold"] = platform_n

    def run_query(self):
        idx = self.query_selector.currentIndex()
        role = self.input_widgets["role"].currentText()
        result = []
        columns = []

        try:
            if idx == 0:
                start_year = int(self.input_widgets["start_year"].text())
                end_year = int(self.input_widgets["end_year"].text())
                top_n = int(self.input_widgets["top_n"].text())
                result = queries.q_dev_pub_revenues(self.cursor, role, start_year, end_year, top_n)
                columns = ["Name", "Total Revenue"]

            elif idx == 1:
                threshold = float(self.input_widgets["rating_threshold"].text())
                result = queries.q_dev_pub_rating(self.cursor, role, threshold)
                columns = ["Name", "High Rated Games"]

            elif idx == 2:
                threshold = int(self.input_widgets["platform_threshold"].text())
                result = queries.q_dev_pub_compatibility(self.cursor, role, threshold)
                columns = ["Name", "Platform Count"]

            else:
                result = []
                columns = []

            # ==== Display table ====
            if hasattr(result, "fetchall"):
                rows = result.fetchall()
            else:
                rows = result

            if not rows:
                self.result_output.setText("No results found.")
                self.table_output.clear()
                self.table_output.setRowCount(0)
                self.table_output.setColumnCount(0)
                return

            self.table_output.clear()
            self.table_output.setRowCount(len(rows))
            self.table_output.setColumnCount(len(columns))
            self.table_output.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table_output.setItem(i, j, item)

            self.table_output.resizeColumnsToContents()
            self.result_output.clear()

        except ValueError:
            self.result_output.setStyleSheet("color: red")
            self.result_output.setText("Please enter valid numeric input.")
        except Exception as e:
            self.result_output.setStyleSheet("color: red")
            self.result_output.setText(f"Query failed: {e}")

    def go_back(self):
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Intro()
    window.show()
    sys.exit(app.exec())


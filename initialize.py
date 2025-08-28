import mysql.connector
import os, csv

def create(cursorObject, database):
    try:
        # create database
        cursorObject.execute(f"CREATE DATABASE IF NOT EXISTS {database};")
        cursorObject.execute(f"USE {database};")

        # create tabels
        TABLES = []

        TABLES.append("""
        CREATE TABLE Games (
            GameID INT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Description TEXT,
            ReleaseDate DATE NOT NULL,
            LanguageSupport VARCHAR(255),
            Genre VARCHAR(100),
            RequireAge INT DEFAULT NULL,
            Tags VARCHAR(255),
            UnitsSold INT
        );
        """)

        TABLES.append("""
        CREATE TABLE Achievement (
            GameID INT,
            AchievementID INT,
            Name VARCHAR(255),
            Description TEXT,
            PRIMARY KEY (GameID, AchievementID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE DLC (
            GameID INT,
            DLCID INT,
            Name VARCHAR(255),
            ReleaseDate DATE,
            Price DECIMAL(10, 2),
            Description TEXT,
            PRIMARY KEY (GameID, DLCID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Player (
            UserID INT PRIMARY KEY,
            UserName VARCHAR(255),
            Email VARCHAR(255),
            Region VARCHAR(100),
            JoinDate DATE,
            Level INT,
            TotalPlayTime INT,
            GamesOwned INT
        );
        """)

        TABLES.append("""
        CREATE TABLE Platform (
            PlatformID INT PRIMARY KEY,
            PlatformName VARCHAR(255),
            Manufacturer VARCHAR(255),
            TotalGameNumber INT,
            WebSite VARCHAR(255)
        );
        """)

        TABLES.append("""
        CREATE TABLE Developer (
            DeveloperID INT PRIMARY KEY,
            DeveloperName VARCHAR(255),
            Address VARCHAR(255),
            FoundedYear INT,
            Country VARCHAR(100),
            Website VARCHAR(255)
        );
        """)

        TABLES.append("""
        CREATE TABLE Publisher (
            PublisherID INT PRIMARY KEY,
            PublisherName VARCHAR(255),
            Address VARCHAR(255),
            FoundedYear INT,
            Country VARCHAR(100),
            Website VARCHAR(255),
            Description TEXT
        );
        """)

        TABLES.append("""
        CREATE TABLE Player_Platform_Games_Play (
            GameID INT,
            PlatformID INT,
            PlayerID INT,
            TotalPlayingTime INT,
            LastPlayTime DATETIME,
            PurchaseTime DATETIME,
            PurchasePrice DECIMAL(10, 2),
            Review TEXT,
            Rating INT CHECK (Rating BETWEEN 1 AND 10),
            PRIMARY KEY (GameID, PlatformID, PlayerID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PlatformID) REFERENCES Platform(PlatformID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PlayerID) REFERENCES Player(UserID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Player_Unlock_Achievement (
            PlayerID INT,
            GameID INT,
            AchievementID INT,
            GainTime DATE,
            PRIMARY KEY (PlayerID, GameID, AchievementID),
            FOREIGN KEY (GameID, AchievementID) REFERENCES Achievement(GameID, AchievementID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PlayerID) REFERENCES Player(UserID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Player_Use_Platform (
            PlayerID INT,
            PlatformID INT,
            RegistrationDate DATETIME,
            TotalTimeSpent INT,       
            PRIMARY KEY (PlayerID, PlatformID),
            FOREIGN KEY (PlatformID) REFERENCES Platform(PlatformID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PlayerID) REFERENCES Player(UserID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Player_Friends (
            Player1ID INT,
            Player2ID INT,
            StartDate DATETIME,
            MutualTime INT,
            PRIMARY KEY (Player1ID, Player2ID),
            FOREIGN KEY (Player1ID) REFERENCES Player(UserID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Player2ID) REFERENCES Player(UserID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Platform_Support_Games (
            GameID INT,
            PlatformID INT,
            Price DECIMAL(10, 2),
            IssuedTime DATE,
            Rating DECIMAL(3, 1),
            PRIMARY KEY (GameID, PlatformID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PlatformID) REFERENCES Platform(PlatformID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Developer_Games (
            GameID INT,
            DeveloperID INT,
            DevelopeStartYear YEAR,
            DevelopeFinishYear YEAR,
            DevelopeCost DECIMAL(12, 2),
            PRIMARY KEY (GameID, DeveloperID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (DeveloperID) REFERENCES Developer(DeveloperID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        TABLES.append("""
        CREATE TABLE Publisher_Games (
            GameID INT,
            PublisherID INT,
            PublishYear YEAR,
            PublishCost DECIMAL(12, 2),
            PRIMARY KEY (GameID, PublisherID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PublisherID) REFERENCES Publisher(PublisherID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        for sql in TABLES:
            cursorObject.execute(sql)

        print("Database and tables created successfully.")

    except mysql.connector.Error as err:
        print("Error:", err)


def insert(cursorObject, dataset, table):
    """
    Insert multiple records into a database table.

    Parameters:
    cursorObject: A database cursor object.
    dataset: A list of dictionaries, each representing a row to insert.
    table: The name of the table to insert data into.
    """
    if not dataset:
        print("No data provided.")
        return

    # Extract columns from the first record
    columns = dataset[0].keys()
    column_names = ", ".join(f"`{col}`" for col in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    # Construct the SQL query
    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

    # Prepare values as a list of tuples
    values = [tuple(record[col] for col in columns) for record in dataset]

    try:
        cursorObject.executemany(sql, values)
        print(f"{cursorObject.rowcount} records inserted into '{table}'.")
    except Exception as e:
        print("Error during insertion:", e)


def load_csv_data(folder_path):
    data_batches = []

    def clean(val):
        return None if val == '' else val

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            table_name = filename[:-4]
            file_path = os.path.join(folder_path, filename)
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                dataset = []
                for row in reader:
                    cleaned_row = {key: clean(value) for key, value in row.items()}
                    dataset.append(cleaned_row)
                data_batches.append((table_name, dataset))
    return data_batches


def initialize(cursorObject, database):
    create(cursorObject, database)
    folder_path = './data'
    data_batches = load_csv_data(folder_path)

    insertion_order = [
        "Games", "Player", "Platform", "Developer", "Publisher",
        "Achievement", "DLC",
        "Developer_Games", "Publisher_Games", "Platform_Support_Games",
        "Player_Platform_Games_Play", "Player_Unlock_Achievement",
        "Player_Use_Platform", "Player_Friends"
    ]

    data_batches.sort(key=lambda x: insertion_order.index(x[0]) if x[0] in insertion_order else float('inf'))

    for table_name, dataset in data_batches:
        print(f"Inserting into table: {table_name}")
        insert(cursorObject, dataset, table_name)


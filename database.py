# database.py
import sqlite3

class EmotionDatabase:
    def __init__(self, db_name='userdata.db'):
        self.db_connection = sqlite3.connect(db_name)
        self.db_cursor = self.db_connection.cursor()
        self.setup_database()

    def setup_database(self):
        # Create the users table if it doesn't exist
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                location TEXT,
                other_info TEXT
            )
        ''')
        self.db_connection.commit()

    def insert_user_data(self, username, location, other_info):
        # Insert user data into the users table
        self.db_cursor.execute('''
            INSERT INTO users (username, location, other_info)
            VALUES (?, ?, ?)
        ''', (username, location, other_info))
        self.db_connection.commit()

    def get_any_user_data(self):
        # Retrieve user data based on the username
        self.db_cursor.execute('''SELECT * FROM users where username IS NOT NULL  LIMIT 1''')
        return self.db_cursor.fetchone()

    # Other database-related methods can be added as needed

    def close_connection(self):
        # Close the database connection
        self.db_connection.close()

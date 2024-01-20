# database.py
import sqlite3
import datetime

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
        self.db_cursor.execute('''
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATETIME NOT NULL,
                        emotion_value TEXT                        
                    )
                ''')
        self.db_connection.commit()

    def insert_user_data(self, username, location, other_info):
        try:
            # Insert user data into the users table
            self.db_cursor.execute('''
                INSERT INTO users (username, location, other_info)
                VALUES (?, ?, ?)
            ''', (username, location, other_info))
            self.db_connection.commit()
            return True 
        except Exception as e:
            # print(f"Error inserting user data: {e}")
            return False

    def update_user_by_id(self, user_id, new_username, new_location, new_other_info):
        try:
            # Update user data in the users table based on the ID
            self.db_cursor.execute('''
                UPDATE users
                SET username=?, location=?, other_info=?
                WHERE id=?
            ''', (new_username, new_location, new_other_info, user_id))
            self.db_connection.commit()
            return True  # Indicate successful update
        except Exception as e:
            # Handle the exception (print or log it)
            print(f"Error updating user data: {e}")
            return False
    
    def get_any_user_data(self):
        # Retrieve the last added user data
        self.db_cursor.execute('''SELECT * FROM users WHERE username IS NOT NULL ORDER BY id DESC LIMIT 1''')
        return self.db_cursor.fetchone()

    def get_history(self):
        # retrive all history
        self.db_cursor.execute('''SELECT * FROM history''')
        return self.db_cursor.fetchall()

    def insert_history_entry(self, emotion_value):
        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert data into the "history" table
        self.db_cursor.execute('''
               INSERT INTO history (date, emotion_value)
               VALUES (?, ?)
           ''', (current_datetime, emotion_value))

        # Commit the changes to the database
        self.db_connection.commit()

    def get_history(self):
        # Retrieve the top 5 most recent history entries
        self.db_cursor.execute('''
            SELECT * FROM history
            ORDER BY date DESC
            LIMIT 5
        ''')
        recent_history_entries = self.db_cursor.fetchall()

        return recent_history_entries

    # Other database-related methods can be added as needed
    def close_connection(self):
        # Close the database connection
        self.db_connection.close()

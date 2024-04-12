import sqlite3


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
           login TEXT PRIMARY KEY,
           hashed_password TEXT);
        """)

    def _already_exists(self, login):
        self.cursor.execute("SELECT * FROM users WHERE login = ?;", (login,))
        if self.cursor is not None:
            return True

    def add_user(self, login, hashed_password):
        if self._already_exists(login):
            print('User already exists')
            return False
        self.cursor.execute("INSERT INTO users(login, hashed_password) VALUES(?, ?);", (login, hashed_password))
        self.connection.commit()

    def get_password(self, login):
        self.cursor.execute("SELECT hashed_password FROM users WHERE login =?;", (login,))
        if self.cursor is not None:
            return self.cursor.fetchone()[0]

    def finish_connection(self):
        self.connection.close()


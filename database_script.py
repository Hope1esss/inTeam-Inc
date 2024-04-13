import sqlite3
import errors


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
           login TEXT PRIMARY KEY,
           password TEXT);
        """)

    def add_user(self, login, password):
        try:
            self.cursor.execute("INSERT INTO users(login, password) VALUES(?, ?);", (login, password))
        except sqlite3.IntegrityError as exc:
            raise errors.UserAlreadyExistsError("User already exists") from exc
        self.connection.commit()

    def get_password(self, login):
        try:
            password = self.cursor.execute("SELECT password FROM users WHERE login =?;", (login,)).fetchone()[0]
        except TypeError:
            return False
        return password

    def get_login(self, login):
        try:
            login = self.cursor.execute("SELECT login FROM users WHERE login =?;", (login,)).fetchone()[0]
        except TypeError:
            return False
        return login

    def finish_connection(self):
        self.connection.close()

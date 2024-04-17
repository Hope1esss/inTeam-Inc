import bcrypt

from . import alchemy_db_methods
from . import errors


class AuthenticationSystem:
    def __init__(self):
        self.db = alchemy_db_methods.AlchemyDB()

    def registration(self, login, password):
        self.db.add_user(login, password)

    def login(self, login, password):
        self.db.get_login(login)
        db_password = self.db.get_password(login)
        if not bcrypt.checkpw(password.encode("utf-8"), db_password):
            raise errors.WrongPasswordError("Неверный пароль.")

    def logout(self):
        self.db.finish_connection()

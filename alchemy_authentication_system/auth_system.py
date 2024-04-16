import bcrypt

import alchemy_db_methods


class AuthenticationSystem:
    def __init__(self):
        self.db = alchemy_db_methods.AlchemyDB()

    def registration(self, login, password):
        self.db.add_user(login, password)

    def login(self, login, password):
        self.db.get_login(login)
        db_password = self.db.get_password(login)
        return bcrypt.checkpw(password.encode('utf-8'), db_password)

    def logout(self):
        self.db.finish_connection()

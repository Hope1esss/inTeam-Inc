import bcrypt
import database_script


class Encryption:
    def __init__(self, password):
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), self.salt)

    def check_password(self, password):
        if bcrypt.checkpw(password.encode('utf-8'), self.hashed_password):
            return True
        return False

    def get_hashed_password(self):
        return self.hashed_password


class AuthenticationSystem:
    def __init__(self):
        self.database = database_script.Database()

    def adding_user(self, login, password):
        hashed_password = Encryption(password).get_hashed_password()
        self.database.add_user(login, hashed_password)

    def login(self, login, password):
        if self.database.get_login(login) == login and \
                bcrypt.checkpw(password.encode('utf-8'), self.database.get_password(login)):
            return True
        return False

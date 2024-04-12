import database_script
import bcrypt

class Encryption:
    def __init__(self, password):
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(8))
        
import bcrypt


class Encryption:
    def __init__(self, input_password):
        self.hashed_password = bcrypt.hashpw(
            input_password.encode("utf-8"), bcrypt.gensalt()
        )

    def get_hashed_password(self):
        return self.hashed_password

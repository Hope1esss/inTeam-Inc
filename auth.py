import database
import bcrypt

class User:
    def __init__(self, login, password):
        self.__account = {login: {"password": password, "verification": True}}

    def get_login(self):
        return list(self.__account.keys())[0]

    def get_password(self):
        login = self.get_login()
        return self.__account[login]["password"]

input_login = input()
input_password = input()

users_data = [User(input_login, input_password)]

"hyi.mne.v.rot@yandex.ru"
"qwerty123"

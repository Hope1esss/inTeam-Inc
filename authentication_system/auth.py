"""
Этот модуль предоставляет классы и методы для управления аутентификацией пользователей и
шифрованием паролей.

Классы
-------
Encryption
    Обрабатывает шифрование и проверку паролей с использованием bcrypt.
AuthenticationSystem
    Управляет аутентификацией пользователей, включая добавление новых пользователей с
    зашифрованными паролями и проверку входов в систему.

Класс `Encryption` использует bcrypt для безопасного хеширования и проверки паролей,
в то время как класс `AuthenticationSystem` взаимодействует с базой данных для
хранения и проверки учетных данных пользователей.

Примеры
--------
Чтобы создать новый экземпляр AuthenticationSystem и использовать его для добавления нового
пользователя и проверки входа:

>>> auth_system = AuthenticationSystem()
>>> auth_system.adding_user('ilya.goat@yandex.ru', 'iaml00s3r')
>>> auth_system.login('ilya.goat@yandex.ru', 'iaml00s3r')
True

Примечания
-----
Убедитесь, что модуль `database_script` доступен в той же среде, что и этот модуль,
поскольку `AuthenticationSystem` зависит от него для управления данными пользователя.
"""

import bcrypt
import database_script


class Encryption:
    """
    Класс для работы с шифрованием паролей с использованием bcrypt.

    Параметры
    ----------
    password : str
        Пароль в открытом виде, который будет зашифрован.

    Атрибуты
    ----------
    salt : bytes
        Криптографическая "соль", сгенерированная для хеширования.
    hashed_password : bytes
        Хешированный пароль, сохраненный в виде байтов.

    Методы
    -------
    check_password(password)
        Проверяет пароль в открытом виде против зашифрованного хеша.
    get_hashed_password()
        Возвращает зашифрованный пароль.
    """

    def __init__(self, password):
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), self.salt)

    def check_password(self, password):
        """
        Проверяет пароль в открытом виде против зашифрованного хеша.

        Параметры
        ----------
        password : str
            Пароль в открытом виде для проверки.

        Возвращает
        -------
        bool
            True, если пароль совпадает с хешем, иначе False.
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password)

    def get_hashed_password(self):
        """
        Возвращает зашифрованный пароль.

        Возвращает
        -------
        bytes
            Хешированный пароль, сохраненный в виде байтов.
        """
        return self.hashed_password


class AuthenticationSystem:
    """
    Класс, отвечающий за управление аутентификацией пользователей.

    Атрибуты
    ----------
    database : Database
        Экземпляр Database из модуля database_script,
        используемый для управления данными пользователя.

    Методы
    -------
    adding_user(login, password)
        Добавляет нового пользователя с зашифрованным паролем в базу данных.
    login(login, password)
        Проверяет учетные данные пользователя и возвращает True, если вход успешен.
    """

    def __init__(self):
        self.database = database_script.Database()

    def adding_user(self, login, password):
        """
        Добавляет нового пользователя с зашифрованным паролем в базу данных.

        Параметры
        ----------
        login : str
            Логин пользователя.
        password : str
            Пароль пользователя в открытом виде, который будет зашифрован перед сохранением.

        Возвращает
        -------
        None
        """
        hashed_password = Encryption(password).get_hashed_password()
        self.database.add_user(login, hashed_password)

    def login(self, login, password):
        """
        Проверяет учетные данные пользователя и возвращает True, если вход успешен.

        Параметры
        ----------
        login : str
            Логин пользователя.
        password : str
            Пароль пользователя в открытом виде для проверки.

        Возвращает
        -------
        bool
            True, если учетные данные пользователя верны и вход выполнен успешно, иначе False.
        """
        user_login = self.database.get_login(login)
        user_password = self.database.get_password(login)
        return user_login == login and bcrypt.checkpw(password.encode('utf-8'), user_password)

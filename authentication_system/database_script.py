"""
Этот модуль предоставляет класс Database для управления базой данных пользователей.
Класс позволяет добавлять новых пользователей, получать пароли и логины, а также
закрывать соединение с базой данных.

Классы
-------
Database
    Управляет соединением с базой данных SQLite и предоставляет методы для работы с
    таблицей пользователей.

Исключения
----------
UserAlreadyExistsError
    Вызывается, когда попытка добавить пользователя с существующим логином.
"""

import sqlite3
from . import errors


class Database:
    """
    Класс для управления базой данных пользователей через SQLite.

    При инициализации создает подключение к базе данных и таблицу пользователей,
    если она не существует.

    Атрибуты
    ----------
    connection : Connection
        Объект подключения к базе данных SQLite.
    cursor : Cursor
        Объект курсора для выполнения SQL команд.

    Методы
    -------
    add_user(login, password)
        Добавляет нового пользователя в базу данных.
    get_password(login)
        Возвращает пароль пользователя по логину.
    get_login(login)
        Проверяет наличие логина в базе данных.
    finish_connection()
        Закрывает подключение к базе данных.
    """

    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
           login TEXT PRIMARY KEY,
           password TEXT);
        """)

    def add_user(self, login, password):
        """
        Добавляет нового пользователя в базу данных.

        Параметры
        ----------
        login : str
            Логин нового пользователя.
        password : str
            Пароль нового пользователя.

        Исключения
        ----------
        UserAlreadyExistsError
            Вызывается, если пользователь с таким логином уже существует.
        """

        try:
            self.cursor.execute("INSERT INTO users(login, password) VALUES(?, ?);",
                                (login, password))
        except sqlite3.IntegrityError as exc:
            raise errors.UserAlreadyExistsError(
                f"Имя пользователя {login} уже используется."
            ) from exc
        self.connection.commit()

    def get_password(self, login):
        """
        Возвращает пароль пользователя по его логину.

        Параметры
        ----------
        login : str
            Логин пользователя.

        Возвращает
        -------
        str или bool
            Пароль пользователя или False, если логин не найден.
        """
        try:
            password = self.cursor.execute("SELECT password FROM users WHERE login =?;", \
                                           (login,)).fetchone()[0]
        except TypeError:
            return False
        return password

    def get_login(self, login):
        """
        Проверяет наличие логина в базе данных и возвращает его.

        Параметры
        ----------
        login : str
            Логин для проверки.

        Возвращает
        -------
        str или bool
            Логин, если найден, иначе False.
        """
        try:
            login = self.cursor.execute("SELECT login FROM users WHERE login =?;", \
                                        (login,)).fetchone()[0]
        except TypeError:
            return False
        return login

    def finish_connection(self):
        """
        Закрывает подключение к базе данных.
        """
        self.connection.close()

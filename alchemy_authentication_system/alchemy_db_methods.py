import sqlalchemy
from sqlalchemy.orm import sessionmaker

from . import alchemy_db_init
from . import encryption
from . import errors


class AlchemyDB:
    def __init__(self):
        self.start_session = sessionmaker(bind=alchemy_db_init.engine)
        self.session = self.start_session()

    def add_user(self, login, password):
        try:
            hashed_password = encryption.Encryption(password).get_hashed_password()
            user = alchemy_db_init.User(login=login, password=hashed_password)
            self.session.add(user)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as exc:
            raise errors.UserAlreadyExistsError(
                f"Имя пользователя {login} уже используется."
            ) from exc

    def get_password(self, login):
        user = self.session.query(alchemy_db_init.User).filter_by(login=login).first()
        if user is None:
            raise errors.UserNotFoundError(f"Пользователь {login} не найден.")
        return user.password

    def get_login(self, login):
        user = self.session.query(alchemy_db_init.User).filter_by(login=login).first()
        if user is None:
            raise errors.UserNotFoundError(f"Пользователь {login} не найден.")
        return user.login

    def finish_connection(self):
        self.session.close()

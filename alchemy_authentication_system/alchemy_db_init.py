# Данный скрипт должен вызваться всего один раз для создания таблицы users в БД
# Можно конечно запускать повторно, но ничего не изменится (вроде) :)

import sqlalchemy.orm
from sqlalchemy import Column, String, create_engine

engine = create_engine('sqlite:///database.db')
Base = sqlalchemy.orm.declarative_base()


class User(Base):
    __tablename__ = 'Users'
    login = Column(String, primary_key=True)
    password = Column(String)

    def __repr__(self):
        return f"<User(login={self.login}, password={self.password})>"


Base.metadata.create_all(bind=engine)

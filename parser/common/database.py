from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from common.settings import Settings

Base = declarative_base()


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls) -> "SessionManager":
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:  # type: ignore
        return sessionmaker(self.engine, expire_on_commit=False, autoflush=False)

    def refresh(self) -> None:
        self.engine = create_engine(Settings().database_url, echo=True)


def get_sync() -> Session:
    session_maker = SessionManager().get_session_maker()
    return session_maker()  # type: ignore

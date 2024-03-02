from sqlalchemy.orm import (
    DeclarativeBase, sessionmaker, Mapped, mapped_column
)

from sqlalchemy import create_engine, Engine, BigInteger


class BaseSub(DeclarativeBase):
    pass


class Base(BaseSub):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_sessionmaker(engine: Engine) -> sessionmaker:
    """Create sessionmaker for orm
    Example:
        session = get_sessionmaker(engine)
        
        with Session() as session:
            ...

    Args:
        engine (Engine): Engine for sqlalchemy

    Returns:
        sessionmaker: sessionmaker Class
    """
    return sessionmaker(engine)


def get_engine(url: str, create_new: bool = False) -> Engine:
    """Create Engine and tables for database

    Args:
        url (str): URL for connect database
        create_new (bool, optional): Create new tables or not, default not. Defaults to False.

    Returns:
        Engine: Engine for sqlalchemy
    """
    engine = create_engine(url, echo=True)
    if create_new:
        __init_models(engine)
    return engine


def __init_models(engine: Engine) -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

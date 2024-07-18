from fastapi import Depends
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from sqlmodel import Session, SQLModel, create_engine


from api.config import settings
# from api.public.user.models import User, OAuthAccount

connect_args = {}
engine = create_engine(settings.DATABASE_URI, echo=False,
                       pool_size=20,  # Increase the pool size
                       max_overflow=40,
                       )


def create_db_and_tables(): #TODO
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    pass

def get_session():
    with Session(engine) as session:
        yield session


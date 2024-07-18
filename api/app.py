from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import Settings
from api.database import create_db_and_tables
from api.public import api as public_api
from api.utils.logger import logger_config
from api.utils.mock_data_generator import create_user_and_listings

logger = logger_config(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI): #TODO uncomment to create schema in a db and create mock data
    # create_db_and_tables()
    # await create_user_and_listings()


    logger.info("startup: triggered")

    yield

    logger.info("shutdown: triggered")


def create_app(settings: Settings):
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/",
        description=settings.DESCRIPTION,
        lifespan=lifespan,
    )
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(public_api)

    return app

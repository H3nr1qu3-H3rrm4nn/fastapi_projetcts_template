
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.base import Base
from core.user.user_controller import UserController
from utils.connection_pool import ConnectionPool
from fastapi.middleware.cors import CORSMiddleware
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def wait_for_db(engine, retries: int = 5, delay: float = 1.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.exec_driver_sql("SELECT 1")
            logger.info("Database is ready.")
            return
        except Exception as exc:
            logger.warning("DB not ready (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)
    raise RuntimeError("Database not available after retries")
# Cria as tabelas no banco de dados

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cria tabelas
    engine = ConnectionPool.get_engine()
    await wait_for_db(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        # Shutdown: encerra conexões
        await engine.dispose()

app = FastAPI(
    title="API de Rastreamento de Frota",
    description="API para o TCC de Análise e Desenvolvimento de Sistemas.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # ou liste URLs específicas do seu front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(UserController().route)


@app.get("/tracking_api")
def read_root():
    return {"message": "Bem-vindo à API de Rastreamento!"}


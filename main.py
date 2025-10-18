
from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.base import Base
from core.user.user_controller import UserController
from utils.connection_pool import ConnectionPool

# Cria as tabelas no banco de dados

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cria tabelas
    engine = ConnectionPool.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: fecha conexões
    await engine.dispose()

app = FastAPI(
    title="API de Rastreamento de Frota",
    description="API para o TCC de Análise e Desenvolvimento de Sistemas.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)

app.include_router(UserController().route)


@app.get("/tracking_api")
def read_root():
    return {"message": "Bem-vindo à API de Rastreamento!"}


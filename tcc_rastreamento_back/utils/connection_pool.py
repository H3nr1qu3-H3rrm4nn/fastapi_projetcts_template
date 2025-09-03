from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Importa as configurações, incluindo a URL do banco de dados.
from tcc_rastreamento_back.utils.settings import Settings

# Cria o engine assíncrono do SQLAlchemy.
# A string de conexão foi atualizada em settings.py para usar o driver 'asyncpg'.
async_engine = create_async_engine(
    Settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False, # Defina como True para ver as queries SQL geradas
)

# Cria uma fábrica de sessões assíncronas (AsyncSessionLocal).
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    """
    Função de dependência assíncrona para o FastAPI.
    Garante que uma nova sessão com o banco de dados seja criada para
    cada requisição e fechada corretamente no final.
    """
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def conditional_session():
    """
    Gerenciador de contexto assíncrono para obter uma sessão fora do
    escopo de uma requisição FastAPI.
    """
    async with AsyncSessionLocal() as session:
        yield session

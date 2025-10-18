from contextlib import asynccontextmanager
from os import getenv
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from utils.settings import settings
from utils.context_vars import tenant_id


class ConnectionPool:
    
    username =getenv("POSTGRES_USERNAME", settings.USERNAME)
    password =getenv("POSTGRES_PASSWORD", settings.PASSWORD)
    host =("POSTGRES_HOSTNAME", settings.HOST)
    port = (
        int(getenv("POSTGRES_PORT"))
        if getenv("POSTGRES_PORT")
        else settings.POSTGRES_PORT
    )
    name =getenv("POSTGRES_DB_NAME", settings.DB_NAME)
    encoding = "utf8"

    encoded_password = quote_plus(password)

    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=50,
        max_overflow=10,
    )
    session = None


    # Configuração do sessionmaker assíncrono
    
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True
    )
    
    @staticmethod
    @asynccontextmanager
    async def get_db_session(tenant_flag=True, param_tenant_id=None):
        """
        Fornece uma sessão de banco de dados gerenciada com async with.
        """
        tenant_id_to_use = (
            param_tenant_id if param_tenant_id is not None else tenant_id.get()
        )
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=ConnectionPool.engine
        )
        db_session = SessionLocal()
        async with ConnectionPool.async_session_factory() as session:
            yield session
    

    @staticmethod
    def get_engine():
        """
        Retorna o engine assíncrono para o banco de dados.
        """
        return ConnectionPool.engine

    

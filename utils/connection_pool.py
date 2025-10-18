from contextlib import asynccontextmanager
from os import getenv
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from utils.settings import settings
from utils.context_vars import tenant_id


class ConnectionPool:
    
    username = getenv("POSTGRES_USERNAME", settings.postgres_user)
    password = getenv("POSTGRES_PASSWORD", settings.postgres_password)
    host = getenv("POSTGRES_HOSTNAME", settings.postgres_host)
    port = (
        int(getenv("POSTGRES_PORT"))
        if getenv("POSTGRES_PORT")
        else settings.postgres_port
    )
    name = getenv("POSTGRES_DB_NAME", "tracking_db")
    encoding = "utf8"

    encoded_password = quote_plus(password)

    engine = create_async_engine(
        f"postgresql+asyncpg://{username}:{encoded_password}@{host}:{port}/{name}",
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
    async def tenant_filter_query(original_query_method, tenant_id: str):
        async def filtered_query(*entities, **kwargs):
            query = await original_query_method(*entities, **kwargs)
            if entities:
                entity = entities[0]
                # Check if the entity is a model class or a column of a model class
                if hasattr(entity, "class_"):
                    entity = entity.class_
                # Apply the tenant filter if the entity has a tenant_id attribute
                if hasattr(entity, "tenant_id"):
                    query = query.where(entity.tenant_id == tenant_id)
            return query
 
        return filtered_query
    
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
        if tenant_flag:
            original_query_method = db_session.query
            db_session.query = await ConnectionPool.tenant_filter_query(
                original_query_method, tenant_id_to_use
            )
        async with ConnectionPool.async_session_factory() as session:
            yield session
    

    @staticmethod
    def get_engine():
        """
        Retorna o engine assíncrono para o banco de dados.
        """
        return ConnectionPool.engine

    

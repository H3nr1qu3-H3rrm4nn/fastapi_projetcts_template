from contextlib import asynccontextmanager

from utils.connection_pool import ConnectionPool


@asynccontextmanager

async def conditional_session(provided_session=None, tenant_flag=False):
    if provided_session:
        yield provided_session
    else:
        async with ConnectionPool.get_db_session(tenant_flag=tenant_flag) as db:
            yield db



import logging
import logging.config

import pytz
import yaml
from sqlalchemy import asc, desc,  select

from core.abstract.abstract_repository import AbstractRepository
from core.user.user_model import User
from utils.connection_pool import ConnectionPool
from utils.contexts import conditional_session
from utils.filter_model import FiltersSchema
from utils.format import apply_dynamic_filters
from sqlalchemy.ext.asyncio import AsyncSession

from utils.context_vars import user_id as uid

# configure_mappers()

logger = logging.getLogger(__name__)

# Configuração do fuso horário de São Paulo
sp_tz = pytz.timezone("America/Sao_Paulo")


class UserRepository(AbstractRepository):

    async def find_by_email(self, email: str, session:AsyncSession=None):
        async with conditional_session(session) as db:
            try:
                query = select(User).where(User.email == email)
                result = await db.execute(query)
                user = result.scalars().first()
                return user
            
            except Exception as e:
                logger.error(f"Error finding user by email: {e}")
                return None

    async def is_admin(self, user_id: int, session:AsyncSession=None) -> bool:
        async with conditional_session(session) as db:
            try:
                query = select(User).where(User.id == user_id)
                result = await db.execute(query)
                user = result.scalars().first()
                if user and user.is_admin:
                    return True
                return False
            except Exception as e:
                logger.error(f"Error checking if user is admin: {e}")
                return False


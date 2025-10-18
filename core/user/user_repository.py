import logging
import logging.config

import pytz
import yaml
from sqlalchemy import asc, desc,  select

from core.abstract.abstract_repository import AbstractRepository
from core.user.user_model import User
from utils.connection_pool import ConnectionPool
from utils.filter_model import FiltersSchema
from utils.format import apply_dynamic_filters

from utils.context_vars import user_id as uid

# configure_mappers()

logger = logging.getLogger(__name__)

# Configuração do fuso horário de São Paulo
sp_tz = pytz.timezone("America/Sao_Paulo")


class UserRepository(AbstractRepository):

    pass

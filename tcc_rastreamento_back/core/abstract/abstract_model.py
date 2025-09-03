from datetime import datetime
from time import time
from xmlrpc.client import Boolean
from sqlalchemy import Column, Integer, String, DateTime
from tcc_rastreamento_back.utils.base import Base


class AbstractModel(Base):
    """
    Modelo Abstrato do qual outras classes de modelo podem herdar.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
import logging
import logging.config

import pytz
import yaml
from sqlalchemy import asc, desc, or_, select

from core.collaborator.collaborator_model import Collaborator
from core.person.person_model import Person
from core.role.role_model import Role
from core.role_permission.role_permission_repository import RolePermissionRepository
from core.role_user.role_user_model import RoleUser
from core.user.user_model import User
from utils.connection_pool import ConnectionPool
from utils.format import apply_dynamic_filters
from utils.models.exception_model import ExceptionModel
from utils.models.filter_model import FiltersSchema
from utils.context_vars import user_id as uid

# configure_mappers()

with open("logging.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)

# Configuração do fuso horário de São Paulo
sp_tz = pytz.timezone("America/Sao_Paulo")


class UserRepository:

    async def find_by_email(self, email: str, tenant_id: int = None):
        async with ConnectionPool.get_db_session() as db:
            try:
                query = select(User).where(User.email == email)
                if tenant_id is not None:
                    query = query.where(User.tenant_id == tenant_id)
                result = await db.execute(query)
                data = result.scalar_one_or_none()
                return data
            except Exception as e:
                logger.error(e)
                await db.rollback()

    async def find_all(
        self,
        model: User,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        async with ConnectionPool.get_db_session() as db:
            try:
                query = (
                    select(model.id, Person.name, model.image_src)
                    .outerjoin(Person, Person.id == model.person_id)
                    .where(model.is_active == True)  # noqa: E712
                )
                if filters is not None:
                    query = apply_dynamic_filters(query, model, filters)
                if order_by is not None:
                    column = getattr(model, order_by.lower())
                    if ascending.upper() == "TRUE":
                        query = query.order_by(asc(column))
                    else:
                        query = query.order_by(desc(column))
                result = await db.execute(query)
                data = [{"id": row[0], "name": row[1], "image_src": row[2]} for row in result.all()]
                logger.info("Busca de todas as entidades realizada com sucesso")
                return data
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_REDE Não foi possível realizar a busca de todas as entidades -> {e}"
                )
                raise e

    async def find_all_paginated(
        self,
        model: User,
        start: int,
        limit: int,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        async with ConnectionPool.get_db_session() as db:
            try:
                query = (
                    select(model.id, Person.name, model.email, model.image_src)
                    .outerjoin(Person, Person.id == model.person_id)
                    .where(model.is_active == True)  # noqa: E712
                )
                if filters is not None:
                    query = apply_dynamic_filters(query, model, filters)
                if order_by is not None:
                    column = getattr(model, order_by.lower())
                    if ascending.upper() == "TRUE":
                        query = query.order_by(asc(column))
                    else:
                        query = query.order_by(desc(column))
                query = query.offset(start).limit(limit)
                result = await db.execute(query)
                data = [{"id": row[0], "name": row[1],"email":row[2], "image_src": row[3]} for row in result.all()]
                logger.info("Busca de todas as entidades realizada com sucesso")
                return data

            except ExceptionModel as e:
                await db.rollback()
                logger.error(
                    f"Não foi possível realizar a busca de todas as entidades -> {e}"
                )
                raise e

    def find_all_collaborators(self):
        with ConnectionPool.get_db_session() as db:
            try:
                data = (
                    db.query(User.id)
                    .join(Collaborator, Collaborator.person_id == User.person_id)
                    .all()
                )
                return [d._asdict() for d in data]
            except Exception as e:
                logger.error(e)
                db.rollback()

    def find_all_collaborators_by_department(self, department_id: int):
        with ConnectionPool.get_db_session() as db:
            try:
                data = (
                    db.query(User.id)
                    .join(Collaborator, Collaborator.person_id == User.person_id)
                    .filter(Collaborator.department_id == department_id)
                    .all()
                )
                return [d._asdict() for d in data]
            except Exception as e:
                logger.error(e)
                db.rollback()

    def find_permission(self, hash: str):
        with ConnectionPool.get_db_session() as db:
            try:
                permissions = RolePermissionRepository().find_all_by_user_id(uid.get())
                data = False
                for permission in permissions:
                    if permission.hash == hash:
                        data = True
                logger.info("Busca de entidade realizada com sucesso")
                return data

            except Exception as e:
                db.rollback()
                logger.error(f"EXCEPTION_REDE Não foi possível realizar a busca da entidade -> {e}")
                raise e

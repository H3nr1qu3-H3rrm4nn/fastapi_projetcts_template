import logging
import logging.config
from typing import Generic, TypeVar
import pytz
import yaml
from utils.connection_pool import ConnectionPool
from utils.contexts import conditional_session
from utils.format import create_model_instance, format_update_instance
from utils.exception_model import ExceptionModel

from abc import ABC
from utils.filter_model import FiltersSchema
from core.abstract.abstract_repository import AbstractRepository
from sqlalchemy.ext.asyncio import AsyncSession


sp_tz = pytz.timezone("America/Sao_Paulo")
T = TypeVar("T")

logger = logging.getLogger(__name__)


class AbstractService(Generic[T], ABC):

    async def find_all(
        self,
        model: T,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        data = await AbstractRepository().find_all(
            model=model,
            order_by=order_by,
            ascending=ascending,
            filters=filters,
        )
        return data

    async def find_all_paginated(
        self,
        model: T,
        start: int,
        limit: int,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        data = await AbstractRepository().find_all_paginated(
            model=model,
            start=start,
            limit=limit,
            order_by=order_by,
            ascending=ascending,
            filters=filters,
        )
        return data

    async def find_by_id(self, model: T, id: int):
        data = await AbstractRepository().find_by_id(model=model, id=id)
        if data is None or data == {}:
            raise ExceptionModel(message=f"Entidade {str(id)} não cadastrada", status_code=400)
        return data

    async def save(self, model: T, new_data: T, session=None):

        db_model = create_model_instance(model, new_data)

        if session:
            data = await AbstractRepository().save(db_model=db_model, session=session)

            
        else:

            async with ConnectionPool.get_db_session() as db:

                try:
                    data = await AbstractRepository().save(
                        db_model=db_model,
                        session=db,
                        load_relations=None
                    )

                    await db.commit()                  

                except Exception as e:
                    await db.rollback()
                    raise e
            
        return data

    async def update_by_id(self, model: T, id: int, new_data: T, session:AsyncSession = None):
        new_data = format_update_instance(new_data)
        async with conditional_session(session) as db:
            try:
                data = await AbstractRepository().update_by_id(
                    model=model,
                    id=id,
                    new_data=new_data,
                    session=db,
                )
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_AGRONOVA Não foi possível realizar a operação -> {e}", e
                )
                raise e
        return data

    async def delete_by_id(self, model: T, id: int):
        async with ConnectionPool.get_db_session() as db:
            try:
                data = await AbstractRepository().delete_by_id(
                    model=model,
                    id=id,
                    session=db,
                )
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_AGRONOVA Não foi possível realizar a operação -> {e}", e
                )
                raise e
        return data

    async def deactivate_by_id(self, model: T, id: int):
        data = await AbstractRepository().deactivate_by_id(model=model, id=id)
        return data

    async def activate_by_id(self, model: T, id: int):
        data = await AbstractRepository().activate_by_id(model=model, id=id)
        return data

    async def audit(self, model: T, id: int, start_date=None, end_date=None):
        transactions = await AbstractRepository().find_transactions_by_user_id(id=id, start_date=start_date, end_date=end_date)
        list_result = []
        for transaction in transactions:
            data = AbstractRepository().find_versions_by_transaction_id(model=model, id=transaction.id)
            if data:
                list_result.append(
                    {
                        "data": data[0],
                        "user_id": id,
                        "changes": data[1],
                    }
                )
        return list_result

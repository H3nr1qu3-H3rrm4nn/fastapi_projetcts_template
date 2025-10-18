import logging
import logging.config
from typing import TypeVar


from sqlalchemy import asc, desc
from sqlalchemy_continuum import version_class
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from utils.exception_model import ExceptionModel
from utils.filter_model import FiltersSchema
from utils.connection_pool import ConnectionPool

from utils.contexts import conditional_session
from utils.format import apply_dynamic_filters, serialize_model
import yaml

with open("logging.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)

T = TypeVar("T")

class AbstractRepository:

    async def find_all(
        self,
        model: T,
        order_by: str = None,
        ascending: str = 'true',
        filters: FiltersSchema = None,
    ):
        async with ConnectionPool.get_db_session() as db:
            try:
                # Construção inicial da consulta
                query = select(model).where(model.is_active == True)

                if filters is not None and len(filters.filters) > 0:
                    query = apply_dynamic_filters(query, model, filters)
                if not ascending:
                    ascending = 'true'

                if order_by is not None:
                    column = getattr(model, order_by.lower())
                    query = query.order_by(asc(column) if ascending.upper() == "TRUE" else desc(column))

                query = query.distinct()

                # Execução da consulta
                result = await db.execute(query)
                data = result.scalars().unique()  # Obtém todas as linhas como objetos  

                # Converte os objetos em dicionários
                logger.info("Busca de todas as entidades realizada com sucesso")

                return [serialize_model(d) for d in data] 
            
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_AGRONOVA Não foi possível realizar a busca de todas as entidades -> {e}",
                    exc_info=True,
                )
                raise e
            

    async def find_all_paginated(
        self,
        model: T,
        start: int,
        limit: int,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        async with ConnectionPool.get_db_session() as db:
            try:
                # Construção inicial da consulta
                query = select(model).where(model.is_active == True)

                # Aplicação de filtros dinâmicos, se existirem
                if filters is not None and len(filters.filters) > 0:
                    query = apply_dynamic_filters(query, model, filters)

                # Ordenação da consulta, se especificada
                if order_by is not None:
                    column = getattr(model, order_by.lower())
                    order_clause = asc(column) if ascending and ascending.upper() == "TRUE" else desc(column)
                    query = query.order_by(order_clause)

                # Aplicação de paginação
                query = query.offset(start).limit(limit)

                # Execução da consulta
                result = await db.execute(query)
                data = result.unique().scalars().all()  # Obtém os resultados como objetos do modelo

                # Conversão dos resultados para dicionários
                logger.info("Busca paginada de entidades realizada com sucesso")
                return [serialize_model(d) for d in data] 
            
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"Não foi possível realizar a busca paginada de entidades -> {e}",
                    exc_info=True,
                )
                raise e

    async def find_by_id(self, model: T, id: int, session: AsyncSession = None):

        if session: 
            try:
                # Construção da consulta para buscar por ID
                query = select(model).where(model.id == id)

                # Execução da consulta
                result = await session.execute(query)
                data = result.unique().scalar_one_or_none()  # Obtém o primeiro registro ou None

                logger.info("Busca de entidade realizada com sucesso")

                if data is not None:

                    return data
                
                return None
            
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_AGRONOVA Não foi possível realizar a busca da entidade -> {e}",
                    exc_info=True,
                )
                raise e
            
        else:
            async with ConnectionPool.get_db_session() as db:
                try:
                    # Construção da consulta para buscar por ID
                    query = select(model).where(model.id == id)

                    # Execução da consulta
                    result = await db.execute(query)
                    data = result.unique().scalar_one_or_none()  # Obtém o primeiro registro ou None

                    logger.info("Busca de entidade realizada com sucesso")

                    if data is not None:

                        return data
                    
                    return None
                
                except Exception as e:
                    await db.rollback()
                    logger.error(
                        f"EXCEPTION_AGRONOVA Não foi possível realizar a busca da entidade -> {e}",
                        exc_info=True,
                    )
                    raise e

    async def save(self, db_model: T, session: AsyncSession, load_relations: list[str] = None):
        try:
            # Adiciona o modelo ao contexto da sessão
            session.add(db_model)
            
            # Cria a transação personalizada
            #await create_custom_transaction(session)
            
            # Realiza o flush para persistir as mudanças
            await session.flush()

            logger.info("Entidade criada com sucesso")
              

            if load_relations:
                await session.refresh(db_model, attribute_names=load_relations)
                options = [
                    joinedload(getattr(db_model.__class__, relation)) for relation in load_relations
                ]
                query = select(db_model.__class__).options(*options).where(
                    db_model.__class__.id == db_model.id
                )
                result = await session.execute(query)
                db_model = result.scalars().first()

            
            return db_model
        
        except Exception as e:

            await session.rollback()
            logger.error(f"Não foi possível criar a entidade -> {e}", exc_info=True)
            raise e

    async def update_by_id(self, model: T, id: int, new_data: dict, session: AsyncSession):
        try:
            # Busca a entidade no banco pelo ID
            query = select(model).where(model.id == id)
            result = await session.execute(query)
            data = result.scalar()

            if data:
                # Atualiza os campos fornecidos em new_data
                for key, value in new_data.items():
                    if value is not None:
                        setattr(data, key, value)

                # Cria a transação personalizada
                # await create_custom_transaction(session)

                # Realiza o flush para persistir as alterações
                await session.flush()

                response = data
                logger.info("Entidade atualizada com sucesso")
                
                return response
            else:
                raise ExceptionModel(message="Entidade não encontrada", status_code=400)

        except Exception as e:
            logger.error(f"Não foi possível atualizar a entidade -> {e}", exc_info=True)
            raise e

    async def delete_by_id(self, model: T, id: int, session: AsyncSession = None):
        async with conditional_session(session) as session:
            try:
                # Busca a entidade no banco pelo ID
                query = select(model).where(model.id == id)
                result = await session.execute(query)
                delete_data = result.scalars().first()

                if delete_data:

                    response = delete_data

                    # Remove a entidade do banco
                    await session.delete(delete_data)

                    # Cria a transação personalizada
                    # create_custom_transaction(session)

                    # Persiste a transação
                    if session:
                        await session.flush()
                    else:
                        await session.commit()

                    logger.info("Entidade deletada com sucesso")

                    return serialize_model(response)
                
                else:
                    raise ExceptionModel(message="Entidade não encontrada", status_code=400)
            
            except Exception as e:
                await session.rollback()
                logger.error(f"Não foi possível deletar a entidade -> {e}", exc_info=True)
                raise e

    async def deactivate_by_id(self, model: T, id: int):
        async with ConnectionPool.get_db_session() as session:
            try:
                # Busca a entidade no banco pelo ID
                query = select(model).where(model.id == id)
                result = await session.execute(query)
                data = result.scalars().first()

                if data:
                    # Atualiza o campo `is_active` para False
                    update_stmt = (
                        model.__table__.update()
                        .where(model.id == id)
                        .values(is_active=False)
                    )
                    await session.execute(update_stmt)

                    # Cria a transação personalizada
                    # await create_custom_transaction(session)

                    # Persiste a transação
                    await session.commit()

                    logger.info("Entidade desativada com sucesso")
                    
                    await session.refresh(data)

                    return serialize_model(data)
                else:
                    raise ExceptionModel(message="Entidade não encontrada", status_code=400)
            except Exception as e:
                await session.rollback()
                logger.error(f"Não foi possível desativar a entidade -> {e}", exc_info=True)
                raise e

    async def activate_by_id(self, model: T, id: int):
        async with ConnectionPool.get_db_session() as session:
            try:
                # Busca a entidade no banco pelo ID
                query = select(model).where(model.id == id)
                result = await session.execute(query)
                data = result.scalars().first()

                if data:
                    # Atualiza o campo `is_active` para True
                    update_stmt = (
                        model.__table__.update()
                        .where(model.id == id)
                        .values(is_active=True)
                    )
                    await session.execute(update_stmt)

                    # Cria a transação personalizada
                    # await create_custom_transaction(session)

                    # Persiste a transação
                    await session.commit()

                    logger.info("Entidade ativada com sucesso")

                    await session.refresh(data)
                    
                    return serialize_model(data)
                    
                else:
                    raise ExceptionModel(message="Entidade não encontrada", status_code=400)
            except Exception as e:
                await session.rollback()
                logger.error(f"Não foi possível ativar a entidade -> {e}", exc_info=True)
                raise e

    async def find_versions_by_transaction_id(self, model: T, id: int, session):
        try:
            # Obtenha a classe de versão do modelo
            VersionModel = version_class(model)

            # Construa a consulta assíncrona
            query = select(VersionModel).where(VersionModel.transaction_id == id)
            result = await session.execute(query)
            data = result.scalars().first()

            if data:
                # Retorna os dados serializados e o conjunto de alterações
                return [serialize_model(data), data.changeset]
            else:
                return None
        except Exception as e:
            await session.rollback()
            logger.error(
                f"EXCEPTION_AGRONOVA Não foi possível buscar as versões da transação -> {e}",
                exc_info=True,
            )
            raise e
        


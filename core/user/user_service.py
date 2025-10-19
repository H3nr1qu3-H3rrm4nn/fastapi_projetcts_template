import pytz
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.context import CryptContext
import yaml

from core.abstract.abstract_repository import AbstractRepository
from core.abstract.abstract_service import AbstractService


from core.user.user_model import User, UserCreate, UserLogin, UserUpdate
from core.user.user_repository import UserRepository


from utils.connection_pool import ConnectionPool
from utils.custom_formatter import CustomFormatter
from utils.exception_model import ExceptionModel
from utils.filter_model import FiltersSchema
from utils.format import create_model_instance
import logging

from utils.response_model import ResponseModel
from utils.settings import Settings

logger = logging.getLogger(__name__)
sp_tz = pytz.timezone("America/Sao_Paulo")

class UserService(AbstractService):


    user_id = "unknown_user"

    crypt_context = CryptContext(schemes=["sha256_crypt"])
    
    async def login(self, user: UserLogin, req: Request):
        

        user_db = await UserRepository().find_by_email(
            email=user.email,
        )

        if not user_db or not self.crypt_context.verify(
            user.password,
            user_db.password):
            raise ExceptionModel(status_code=400, message="Usuário ou senha incorreto")


        if user_db.is_active is not True:
            raise ExceptionModel(status_code=401, message="Usuário inativo")
        
        payload = {
            "sub": user_db.email,
            "user": user_db.id,
            "admin": await UserRepository().is_admin(user_db.id),
            "sys": 2
        }

        self.login_user_log(
            user_id_value=f"{user_db.id}"
        )

        logger.info("Usuario logado com sucesso!!")

        access_token = jwt.encode(payload, Settings().SECRET_KEY, Settings().ALGORITHM)

        return access_token


    async def find_by_email(self, email: str):
            data = await UserRepository().find_by_email(email)
            return data

    async def find_by_id(self, model: User, id: int):

        user = await AbstractRepository().find_by_id(model, id)
        if user is None or user == {}:
            raise ExceptionModel(
                message=f"Entidade {str(id)} não cadastrada", status_code=400
            )

        return user

    async def save(self, model: User, new_data: UserCreate):
        """
        Método save sobrescrito para garantir que a senha seja encriptada antes de salvar.
        """

        new_data.password = self.crypt_context.hash(new_data.password)

        db_model = create_model_instance(model, new_data)

        async with ConnectionPool.get_db_session() as db:
            try:
                data = await AbstractRepository().save(db_model=db_model, session=db)

                await db.commit()
                logger.info("Usuário criado com sucesso com senha encriptada")
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_REDE Não foi possível realizar a operação -> {e}", e
                )
                raise e

        return data

    async def update_by_id(self, id: int, model: User, new_data: UserUpdate):
        if new_data.password:
            new_data.password = self.crypt_context.hash(new_data.password)

        response = await self.find_by_id(model=User, id=id)
        response_dict = response.__dict__

        async with ConnectionPool.get_db_session() as db:
            try:
                data = await AbstractRepository().update_by_id(
                    id=id,
                    new_data=new_data.__dict__,
                    model=model,
                    session=db,
                )

                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION Não foi possível realizar a operação -> {e}", e
                )
                raise e
        return data

    async def delete_by_id(self, model: User, id: int):
        response = await super().delete_by_id(model, id)
        return response

    async def find_all(
        self,
        model: User,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        data = await UserRepository().find_all(
            model=model,
            order_by=order_by,
            ascending=ascending,
            filters=filters,
        )
        return data

    async def find_all_paginated(
        self,
        model: User,
        start: int,
        limit: int,
        order_by: str = None,
        ascending: str = None,
        filters: FiltersSchema = None,
    ):
        data = await UserRepository().find_all_paginated(
            model=model,
            start=start,
            limit=limit,
            order_by=order_by,
            ascending=ascending,
            filters=filters,
        )
        return data

    def logout_user_log(self, user_id_value):
        """
        Atualiza o logging para registrar o logout do usuário
        """
        logger.info(f"Usuário {user_id_value} realizou logout")

    def login_user_log(self, user_id_value):
        self.user_id = user_id_value
        self.update_logging_format()

    def update_logging_format(self):
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler.formatter, CustomFormatter):
                handler.formatter.user_id_getter = self.user_id

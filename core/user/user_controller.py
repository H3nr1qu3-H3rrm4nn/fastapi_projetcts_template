import logging
import logging.config
from typing import Annotated

from fastapi import Header, Request

from core.abstract.abstract_controller import AbstractController
from core.token.token_service import TokenService
from core.user.user_model import User, UserLogin, UserCreate, UserUpdate, UserLogout
from core.user.user_service import UserService
import yaml

from utils.response_model import ResponseModel
from utils.context_vars import user_id as context_user_id


logger = logging.getLogger(__name__)

user_service = UserService()

class UserController(AbstractController):
    def __init__(self):
        super().__init__(
            model=User,
            model_create=UserCreate,
            model_update=UserUpdate,
            prefix="/user",
            service=user_service,
            tags=["User"],
            token_service=TokenService(),
        )
        self.get_all()
        self.get_all_paginated()
        self.find_by_id()
        # self.save()
        self.update_by_id()
        self.delete_by_id()
        self.deactivate_by_id()
        self.activate_by_id()
        self.audit()
        self.route.post("/login")(self.login)
        self.route.get("/find_user_by_token")(self.find_user_by_token)
        self.route.post("/save")(self.save)

    async def save(self, new_data: UserCreate):
        """
        Rota save sobrescrita para garantir que a senha seja encriptada.
        """
        response = await user_service.save(
            model=User,
            new_data=new_data
        )
        return ResponseModel(
            success=True,
            message="Usuário criado com sucesso com senha encriptada",
            object=response,
        ).model_response()

    async def login(self, user: UserLogin, req: Request):
        dados_autenticacao = await user_service.login(user=user, req=req)
        return ResponseModel(
            success=True,
            message="Login realizado com sucesso",
            object=dados_autenticacao
        ).model_response()

    async def find_user_by_token(
        self,
        Authorization: Annotated[str | None, Header()],
    ):
        token = await self.validate_token(Authorization)
        response = await user_service.find_by_token(token)
        return ResponseModel(
            success=True,
            message="Usuário retornado com sucesso",
            object=response
        ).model_response()


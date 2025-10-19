from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.token.token_service import TokenService
from utils.filter_model import FiltersSchema
from utils.response_model import ResponseModel

bearer_scheme = HTTPBearer()
class AbstractController:
    def __init__(self, model, model_create, model_update, prefix, service, tags, token_service):
        self.route = APIRouter(prefix=prefix, tags=tags, dependencies=[Depends(self.validate_token)])
        self.model = model
        self.model_create = model_create
        self.model_update = model_update
        self.service = service
        self.token_service = TokenService()

    async def validate_token(
        self,
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    ):
        token = credentials.credentials
        return await self.token_service.validate_token(token=token)

    def get_all(self):

        @self.route.post("/all")
        async def find_all(
            order_by: Annotated[
                str | None, Query(max_length=20, pattern=r"^[^\d]*$")
            ] = None,
            ascending: Annotated[
                str | None, Query(max_length=20, pattern=r"^[^\d]*$")
            ] = None,
            filters: FiltersSchema = None,
        ):
            response = await self.service.find_all(
                model=self.model,
                order_by=order_by,
                ascending=ascending,
                filters=filters,
            )
            return ResponseModel(
                success=True,
                message="Busca de todas as entidades realizada com sucesso",
                object=response,
            ).model_response()

    def get_all_paginated(self):

        @self.route.post("/all/paginated")
        async def find_all_paginated(
            start: int,
            limit: int,
            order_by: Annotated[
                str | None, Query(max_length=20, pattern=r"^[^\d]*$")
            ] = None,
            ascending: Annotated[
                str | None, Query(max_length=20, pattern=r"^[^\d]*$")
            ] = None,
            filters: FiltersSchema = None,
        ):
            response = await self.service.find_all_paginated(
                model=self.model,
                start=start,
                limit=limit,
                order_by=order_by,
                ascending=ascending,
                filters=filters,
            )
            return ResponseModel(
                success=True,
                message="Busca de todas as entidades realizada com sucesso",
                object=response,
            ).model_response()

    def find_by_id(self):

        @self.route.get("/find_by_id/{id}")
        async def find_by_id(id: int):
            response = await self.service.find_by_id(model=self.model, id=id)
            return ResponseModel(
                success=True,
                message="Busca realizada com sucesso",
                object=response,
            ).model_response()

    def save(self):

        @self.route.post("/save")
        async def save(new_data: self.model_create):
            response = await self.service.save(
                model=self.model,
                new_data=new_data
            )
            return ResponseModel(
                success=True,
                message="Inserção realizada com sucesso",
                object=response,
            ).model_response()

    def update_by_id(self):

        @self.route.put("/update_by_id/{id}")
        async def update_by_id(id: int, new_data: self.model_update):
            response = await self.service.update_by_id(
                model=self.model,
                id=id,
                new_data=new_data,
            )
            return ResponseModel(
                success=True,
                message="Atualização realizada com sucesso",
                object=response,
            ).model_response()

    def delete_by_id(self):

        @self.route.delete("/delete_by_id/{id}")
        async def delete_by_id(id: int):
            response = await self.service.delete_by_id(
                model=self.model,
                id=id,
            )
            return ResponseModel(
                success=True,
                message="Exclusão realizada com sucesso",
                object=response,
            ).model_response()

    def deactivate_by_id(self):

        @self.route.post("/deactivate_by_id/{id}")
        async def deactivate_by_id(id: int):
            response = await self.service.deactivate_by_id(
                model=self.model,
                id=id,
            )
            return ResponseModel(
                success=True,
                message="Inativação realizada com sucesso",
                object=response,
            ).model_response()

    def activate_by_id(self):

        @self.route.post("/activate_by_id/{id}")
        async def activate_by_id(id: int):
            response = await self.service.activate_by_id(
                model=self.model,
                id=id,
            )
            return ResponseModel(
                success=True,
                message="Ativação realizada com sucesso",
                object=response,
            ).model_response()

    def audit(self):

        @self.route.get("/audit/{id}")
        async def audit(
            id: int,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
        ):
            response = await self.service.audit(
                model=self.model,
                id=id,
                start_date=start_date,
                end_date=end_date,
            )
            return ResponseModel(
                success=True,
                message="Auditoria realizada com sucesso",
                object=response,
            ).model_response()

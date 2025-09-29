from typing import Type, TypeVar

from fastapi import APIRouter

from tcc_rastreamento_back.utils.models import ResponseModel


TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
class AbstractController:

    def __init__(
        self,
        service: object,
        create: Type[TCreate],
        update: Type[TUpdate],
        prefix: str,
        *,
        tags: list[str] | None = None,
    ) -> None:
        self.service = service
        self.create = create
        self.update = update
        self.prefix = prefix
        self.tags = tags
    
        self.router = APIRouter(prefix=self.prefix, tags=self.tags)
        self._register_routes()

    def _register_routes(self) -> None:
        @self.router.get("", response_model=list[self.create])
        async def list_items():
            result = self.service.list()
            if hasattr(result, "__await__"):
                result = await result
            return result
        
        @self.router.get("/find_by_id/{id}")
        async def find_by_id(id: str):
            result = await self.service.find_by_id(id)
            response = ResponseModel(200, "Item encontrado com sucesso", result)
            return response.response_model()

        @self.router.get("/find_all")
        async def find_all():
            result = await self.service.find_all()
            response = ResponseModel(200, "Itens encontrados com sucesso", result)
            return response.response_model()
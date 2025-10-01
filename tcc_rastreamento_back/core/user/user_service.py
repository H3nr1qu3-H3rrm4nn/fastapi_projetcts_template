import pytz
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.context import CryptContext
import yaml

from core.abstract.abstract_repository import AbstractRepository
from core.abstract.abstract_service import AbstractService
from core.client.client_repository import ClientRepository
from core.collaborator.collaborator_repository import CollaboratorRepository
from core.menu.menu_repository import MenuRepository
from core.role.role_model import Role
from core.role.role_service import RoleService
from core.role_user.role_user_model import RoleUser, RoleUserCreate
from core.role_user.role_user_repository import RoleUserRepository
from core.role_user.role_user_service import RoleUserService
from core.system_module_menu.system_module_menu_model import SystemModuleMenu
from core.system_module_menu.system_module_menu_service import (
    SystemModuleMenuService,
)
from core.tenant.tenant_model import Tenant
from core.tenant.tenant_repository import TenantRepository
from core.user.user_model import User, UserCreate, UserLogin, UserUpdate
from core.user.user_repository import UserRepository
from core.user_device.user_device_model import UserDevice
from core.user_device.user_device_service import UserDeviceService
from utils.config import settings
from utils.connection_pool import ConnectionPool
from utils.custom_formatter import CustomFormatter
from utils.format import create_model_instance
from utils.models.exception_model import ExceptionModel
from utils.models.filter_model import FiltersSchema
from utils.models.response_model import ResponseModel
import logging
import logging.config

with open("logging.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
sp_tz = pytz.timezone("America/Sao_Paulo")

user_device_service = UserDeviceService()

class UserService(AbstractService):

    user_id = "unknown_user"
    tenant_id = "unknown_tenant"

    crypt_context = CryptContext(schemes=["sha256_crypt"])

    async def login(self, user: UserLogin, req: Request):
        

        # host = req.headers["host"]
        # tenant_id = await TenantRepository().find_tenant_id_by_host(host=host)
        # if not tenant_id:
        #     raise ExceptionModel(status_code=404, message="Host não encontrado")

        user_db = await UserRepository().find_by_email(
            email=user.email,
        )

        if not user_db or not self.crypt_context.verify(
            user.password,
            user_db.password):
            raise ExceptionModel(status_code=400, message="Usuário ou senha incorreto")
        
        if user.fcm_token:
            user_device = await user_device_service.find_by_fcm_token(fcm_token=user.fcm_token)
            if not user_device:
                user_device_data = {
                    "fcm_token": user.fcm_token,
                    "user_id": user_db.id,
                    "tenant_id": user_db.tenant_id
                }
                await user_device_service.save(model=UserDevice, new_data=user_device_data)
            else:
                for device in user_device:
                        await user_device_service.delete_by_id(model=UserDevice, id=device.id)
                        
                user_device_data = {
                    "fcm_token": user.fcm_token,
                    "user_id": user_db.id,
                    "tenant_id": user_db.tenant_id
                }
                await user_device_service.save(model=UserDevice, new_data=user_device_data)
        
        
        

        # person_data = None
        # if user_db.role_type == "Colaborador":
        #     person_data = CollaboratorRepository().find_by_person_id(
        #         user_db.person_id, tenant_id.id
        #     )
        # elif user_db.role_type == "Cliente":
        #     person_data = ClientRepository().find_by_person_id(
        #         user_db.person_id, tenant_id=tenant_id.id
        #     )

        if user_db.is_active is not True:
            raise ExceptionModel(status_code=401, message="Usuário inativo")
        
        tenant = await super().find_by_id(model=Tenant, id=user_db.tenant_id)

        payload = {
            "sub": user_db.email,
            "ten": user_db.tenant_id,
            "user": user_db.id,
            "admin": await RoleUserRepository().is_admin(user_db.id),
            "sys": 2,
            "insurance_rate": tenant.insurance_rate if tenant and tenant.insurance_rate else 0.0
        }

        self.login_user_log(
            user_id_value=f"{user_db.id}", tenant_id_value=f"{user_db.tenant_id}"
        )

        logger.info("Usuario logado com sucesso!!")

        access_token = jwt.encode(payload, settings.jwt_key, settings.jwt_algorithm)

        return access_token

    async def logout(self, user_id: int, fcm_token: str = None):
        """
        Realiza logout do usuário removendo dispositivos FCM
        
        Args:
            user_id: ID do usuário
            fcm_token: Token FCM do dispositivo (opcional)
        
        Returns:
            bool: True se logout foi realizado com sucesso
        """
        try:
            if fcm_token:
                # Remove apenas o dispositivo específico com o FCM token fornecido
                user_device = await user_device_service.find_by_fcm_token(fcm_token=fcm_token)
                if user_device:
                    for device in user_device:
                        if device.user_id == user_id:  # Verifica se o dispositivo pertence ao usuário
                            await user_device_service.delete_by_id(model=UserDevice, id=device.id)
                            # logger.info(f"Dispositivo removido para usuário {user_id} com FCM token: {fcm_token[:20]}...")
                            logger.info(f"Dispositivo removido  com FCM token: {fcm_token[:20]}...")
            # else:
            #     # Remove todos os dispositivos do usuário se não foi fornecido FCM token específico
            #     # Como não temos método find_by_user_id, vamos usar uma abordagem alternativa
            #     # Buscar todos os dispositivos e filtrar pelo user_id
            #     try:
            #         async with ConnectionPool.get_db_session() as db:
            #             from sqlalchemy import select
            #             stmt = select(UserDevice).where(UserDevice.user_id == user_id)
            #             result = await db.execute(stmt)
            #             user_devices = result.scalars().all()
                        
            #             for device in user_devices:
            #                 await user_device_service.delete_by_id(model=UserDevice, id=device.id)
                        
            #             if user_devices:
            #                 logger.info(f"Todos os {len(user_devices)} dispositivos removidos para usuário {user_id}")
                        
            #     except Exception as device_error:
            #         logger.warning(f"Erro ao remover dispositivos do usuário {user_id}: {device_error}")
                    # Continue mesmo se houver erro na remoção de dispositivos

            self.logout_user_log(user_id_value=f"{user_id}")
            logger.info(f"Logout realizado com sucesso para usuário {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao realizar logout para usuário {user_id}: {e}")
            raise ExceptionModel(status_code=500, message="Erro interno no logout")

    async def find_by_email(self, email: str, tenant_id: int = None):
            data = await UserRepository().find_by_email(email)
            return data

    async def find_by_token(self, token: dict):
        user_db = await UserRepository().find_by_email(token["sub"])

        permissions = await RoleUserService.find_by_user(self, user_id=user_db.id)

        roles = []
        role_names = []
        if permissions is not None:
            for p in permissions:
                role = await RoleService().find_by_id(model=Role, id=p.role_id)
                roles.append(role)
                role_names.append(role["name"])

        modules = await SystemModuleMenuService().find_all(model=SystemModuleMenu)
        modules_id = []

        for p in modules:
            modules_id.append(p.get('id'))

        menus_list = await SystemModuleMenuService().find_by_modules_ids(
            modules_id=modules_id
        )

        if menus_list == None:
            return JSONResponse(
                status_code=400,
                content=ResponseModel(
                    success=False,
                    object={},
                    message="Não há menus vinculadas aos modulos.",
                ).model_response(),
            )

        menus_ids = []

        for p in menus_list:
            menus_ids.append(p[0])

        menus = await MenuRepository().find_by_role_names(
            role_names=role_names, menus_ids=menus_ids
        )

        if menus == None:
            return JSONResponse(
                status_code=400,
                content=ResponseModel(
                    success=False,
                    object={},
                    message="Não há menus vinculadas a esse usuário.",
                ).model_response(),
            )

        menu_tree = self.build_menu_three(menus)

        response = user_db.repr_by_token()
        response["roles"] = roles
        response["menus"] = menu_tree
        response["insurance_rate"] = token.get("insurance_rate", 0.0)


        return response

    def build_menu_three(self, menu_list):
        menu_dicts = [menu.__dict__ for menu in menu_list]

        menu_dict = {}
        root_menus = []

        # Cria um dicionário para mapear o ID do menu para o menu
        for menu in menu_dicts:
            menu_dict[menu["id"]] = menu

        # Itera sobre cada menu para construir a árvore
        for menu in menu_dicts:
            parent_id = menu["parent_id"]
            if parent_id is None:
                root_menus.append(menu)
            else:
                parent_menu = menu_dict.get(parent_id)
                if parent_menu:
                    if "children" not in parent_menu:
                        parent_menu["children"] = []
                    parent_menu["children"].append(menu)

        # Função recursiva para ordenar a lista de children
        def sort_children(menu):
            if "children" in menu:
                menu["children"] = sorted(
                    menu["children"], key=lambda x: x["order_index"]
                )  # Ordena os children pelo atributo 'name'
                for child in menu["children"]:
                    sort_children(child)

        # Ordena os root menus e seus respectivos children
        root_menus = sorted(
            root_menus, key=lambda x: x["order_index"]
        )  # Ordena os root menus pelo atributo 'name'
        for root_menu in root_menus:
            sort_children(root_menu)

        return root_menus

    async def find_by_id(self, model: User, id: int):

        user = await AbstractRepository().find_by_id(model, id)
        if user is None or user == {}:
            raise ExceptionModel(
                message=f"Entidade {str(id)} não cadastrada", status_code=400
            )
        user_dict = user.__dict__
        user_dict["roles"] = []
        roles_users = await RoleUserRepository.find_by_user(self, user_id=id)

        if roles_users is None:
            roles_users = []

        for roles_user in roles_users:
            r = await RoleService().find_by_id(model=Role, id=roles_user.role_id)
            user_dict["roles"].append(r)
        user_dict["person"] = (
            await CollaboratorRepository().find_by_person_id(person_id=user_dict["person_id"],)
        )
        return user

    async def save(self, model: User, new_data: UserCreate):
        """
        Método save sobrescrito para garantir que a senha seja encriptada antes de salvar.
        """
        # Encripta a senha antes de salvar
        new_data.password = self.crypt_context.hash(new_data.password)

        db_model = create_model_instance(model, new_data)

        async with ConnectionPool.get_db_session() as db:
            try:
                data = await AbstractRepository().save(db_model=db_model, session=db)

                # Salva as roles do usuário se existirem
                if new_data.roles is not None and len(new_data.roles) > 0:
                    for role in new_data.roles:
                        role_user = RoleUserCreate(role_id=role["id"], user_id=data.id)
                        db_model_role = create_model_instance(RoleUser, role_user)
                        await AbstractRepository().save(db_model=db_model_role, session=db)

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

                if len(response_dict['roles']) > 0:
                    for role in response_dict["roles"]:
                        await RoleUserRepository().delete_by_user_id(id=id)

                    for role in new_data.roles:
                        role_user = await RoleUserCreate(role_id=role["id"], user_id=data["id"])
                        db_model = create_model_instance(RoleUser, role_user)
                        await AbstractRepository().save(db_model=db_model, session=db)

                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"EXCEPTION_REDE Não foi possível realizar a operação -> {e}", e
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

    def login_user_log(self, user_id_value, tenant_id_value):
        self.user_id = user_id_value
        self.tenant_id = tenant_id_value
        self.update_logging_format()

    def update_logging_format(self):
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler.formatter, CustomFormatter):
                handler.formatter.user_id_getter = self.user_id
                handler.formatter.tenant_id_getter = self.tenant_id

    def find_permission(self, hash: str):
        data = UserRepository().find_permission(hash)
        return data
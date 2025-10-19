from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

from core.user.user_service import UserService
from utils.settings import settings
from utils.response_model import ResponseModel
from utils.context_vars import admin, user_id

app = FastAPI()


class JWTMiddleware(BaseHTTPMiddleware):

    allowed_paths = [
        "/health",
        "/docs",
        "/openapi.json",
        "/user/login"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Verificar rotas permitidas - usar startswith para permitir subrotas
        if any(request.url.path.startswith(path) for path in self.allowed_paths):
            return await call_next(request)

        try:
            token = request.headers.get("Authorization")
            token = jwt.decode(
                token.removeprefix("Bearer "), settings.SECRET_KEY, settings.ALGORITHM
            )
            request.scope["headers"].append((b"email", str(token["sub"]).encode()))
            request.scope["headers"].append((b"user", str(token["user"]).encode()))
            user_id.set(token["user"])
            admin.set(token["admin"])


            user_db = await UserService().find_by_email(token["sub"])
            if user_db is None:
                return JSONResponse(
                    status_code=401,
                    content=ResponseModel(
                        success=False, object={}, message="Usuário não encontrado!"
                    ).model_response(),
                )
            elif not user_db.is_active:
                return JSONResponse(
                    status_code=401,
                    content=ResponseModel(
                        success=False, object={}, message="Usuário inativo!"
                    ).model_response(),
                )

        except Exception as e:
            return JSONResponse(
                status_code=401,
                content=ResponseModel(
                    success=False,
                    object={},
                    message="Token de acesso inválido ou não enviado!",
                ).model_response(),
            )

        response = await call_next(request)
        return response


app.add_middleware(JWTMiddleware)

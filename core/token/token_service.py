from http.client import HTTPException
from jose import JWTError, jwt
from utils.settings import Settings
from fastapi import status

from utils.context_vars import (
    user_id as ctx_user_id,
)


class TokenService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

    async def validate_token(self, token: str | None) -> str:
        """
        Recebe o header Authorization (opcionalmente com 'Bearer '),
        valida o JWT e retorna o token limpo. Preenche context vars se claims existirem.
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ausente",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_str = token[7:].strip() if token.lower().startswith("bearer ") else token.strip()

        try:
            payload = jwt.decode(
                token_str,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
                options={"verify_aud": False},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Popular context vars se presentes
        uid = payload.get("sub") or payload.get("user_id")
        if uid is not None:
            ctx_user_id.set(uid)

        return token_str
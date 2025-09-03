from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from tcc_rastreamento_back.utils.settings import settings
from tcc_rastreamento_back.utils.connection_pool import get_db
from tcc_rastreamento_back.core.user.user_repository import UserRepository
from tcc_rastreamento_back.core.user.user_model import Usuario

# Define o esquema de autenticação OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/usuarios/token")

def create_access_token(data: dict) -> str:
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """
    Dependência para validar o token e obter o usuário atual.
    Será usada para proteger os endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    repo = UserRepository()
    user = repo.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
from typing import List
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from core.abstract.abstract_model import AbstractModel
from utils.base import Base
from utils.validations import strip_special_chars, validate_url



class User(Base, AbstractModel):
    __tablename__ = "user"

    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    image_src = Column(String, nullable=True)
    is_admin = Column(Boolean)

class UserLogin(BaseModel):
    email: str = Field(
        default="admin@tracker.com",
        max_length=100,
        min_length=5,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    )
    password: str = Field(
        default="tracker2025",
        max_length=250,
        min_length=10,
    )
    fcm_token : str = Field(default=None)


class UserCreate(BaseModel):
    email: str = Field(
        ...,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    )
    password: str = Field(
        ...,
        max_length=250,
        min_length=10,
    )
    name: str = Field(default="Dev", max_length=100, min_length=1)
    image_src: str | None = Field(
        default=None,
        max_length=500,
        min_length=10,
    )
    is_admin: bool = Field(default=False)

    _validate_name = field_validator("name")(lambda v: strip_special_chars(v))
    _validate_image_src = field_validator("image_src")(lambda v: validate_url(v))


class UserUpdate(BaseModel):
    email: str | None = Field(
        default=None,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    )
    password: str | None = Field(default=None, max_length=250)
    name: str | None = Field(default=None, max_length=100, min_length=5)
    image_src: str | None = Field(default=None, max_length=500)
    is_admin: bool | None = Field(default=None)

    _validate_name = field_validator("name")(lambda v: strip_special_chars(v))
    _validate_image_src = field_validator("image_src")(lambda v: validate_url(v))


class UserLogout(BaseModel):
    fcm_token: str | None = Field(
        default=None,
        max_length=500,
        description="Token FCM do dispositivo específico (opcional)"
    )

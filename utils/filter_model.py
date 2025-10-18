
from typing import List
from pydantic import BaseModel, Field


class FiltersSchema(BaseModel):

    attribute: str = Field(..., max_length=100)
    primary_value: str = Field(..., max_length=100)
    secondary_value: str | None = Field(default=None, max_length=100)
    operator: str = Field(..., max_length=100)
    condition: str = Field(..., max_length=100)


class FiltersSchema(BaseModel):

    filters: List[FiltersSchema] = Field(default_factory=list)

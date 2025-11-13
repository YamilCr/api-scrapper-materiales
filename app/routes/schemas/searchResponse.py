from pydantic import BaseModel, conint, Field, ValidationError
from typing import List
from .productsResponse import ProductResponse


class SearchResponse(BaseModel):
    query: str = Field(..., description="Término de búsqueda")
    total: conint(ge=0) = Field(..., description="Cantidad total de productos encontrados")
    items: List[ProductResponse] = Field(..., description="Lista de productos encontrados")

class SearchParams(BaseModel):
    search: str
    limit: conint(ge=1, le=100) = 30
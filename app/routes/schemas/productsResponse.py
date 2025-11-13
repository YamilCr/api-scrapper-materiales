from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ProductResponse(BaseModel):
    product_id: Optional[str] = Field(None, description="ID del producto (puede ser null)")
    name: str = Field(..., description="Nombre del producto")
    brandName: Optional[str] = Field(None, description="Marca del producto")
    category: Optional[str] = Field(None, description="Categoría del producto")
    price_number: float = Field(..., description="Precio numérico")
    price_short: str = Field(..., description="Precio formateado")
    stock: int = Field(..., ge=0, description="Cantidad en stock")
    source: str = Field(..., description="Fuente del producto")
    image_url: HttpUrl = Field(..., description="URL de imagen del producto")
    link: HttpUrl = Field(..., description="URL al detalle del producto")
    logo: Optional[HttpUrl] = Field(None, description="Logo del proveedor")
    discountPercentage: Optional[float] = Field(None, description="Porcentaje de descuento si aplica")

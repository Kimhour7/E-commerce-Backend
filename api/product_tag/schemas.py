from pydantic import BaseModel

class ProductTagSchemas(BaseModel):
    name: str

    class Config:
        from_attributes = True
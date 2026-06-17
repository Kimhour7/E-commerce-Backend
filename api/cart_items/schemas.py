from pydantic import BaseModel

class cart_item_schema(BaseModel):
    cart_id     : str
    product_id  : str
    quantity    : int
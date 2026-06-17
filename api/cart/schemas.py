from pydantic import BaseModel
class cartSchema(BaseModel):
    user_id     : str
    total_price : float
    status      : str
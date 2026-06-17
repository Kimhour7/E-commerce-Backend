

from typing import List

from fastapi import Depends

from api.cart_items.models import TBL_CART_ITEMS
from api.product.models import TBL_PRODUCT
from api.user.models import TBL_USER
from core.custom_id import generate_prefixed_id
from core.db import get_db
from core.permission import AdminPermission
from core.securerity import User

from .schemas import *
from api.cart.models import *
from main import app
from sqlalchemy.orm import Session
from datetime import datetime

@app.post("/cart_items/insert", tags=["Cart Item"])
def cart(
cart        : List[cart_item_schema],
current_user: User = Depends(AdminPermission),
db          : Session = Depends(get_db),
)           : 
    items = []
    
    for i in cart: 
        get_product         = db.query(TBL_PRODUCT).filter(TBL_PRODUCT.id == i.product_id).first()
        sub_total_calculate = 0

        sub_total_calculate = get_product.price * i.quantity

        new_cart_items = TBL_CART_ITEMS(
            id         = generate_prefixed_id(db=db, model=TBL_CART_ITEMS, prefix="ITEM"),
            cart_id    = i.cart_id,
            product_id = i.product_id,
            quantity   = i.quantity,
            sub_total  = sub_total_calculate,
            created_by = current_user.id,
            updated_by = current_user.id,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        items.append(new_cart_items)
    
    db.add_all(items)
    db.commit()
    
    return [{
        "status" : 200,
        "message": "Data fetch successfully hx.",
        "item"   : [{
            "cart_id"   : i.cart_id,
            "product_id": i.product_id,
            "quantity"  : i.quantity,
            "sub_total" : sub_total_calculate,
            "created_by": current_user.id,
            "updated_by": current_user.id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in cart]
    }]

@app.get("/cart_items", tags=["Cart Item"])
def cart(
current_user: User = Depends(AdminPermission),
db          : Session = Depends(get_db),
)           : 
    cart_query = (
        db.query(TBL_CART_ITEMS)
        .join(TBL_CART, TBL_CART.id == TBL_CART_ITEMS.cart_id)
        .join(TBL_USER, TBL_USER.id == TBL_CART.user_id)
        .filter(TBL_USER.id == current_user.id)
        .all()
    )

    sub_items = [{
        "product_id": i.product.id,
        "quantity"  : i.quantity,
        "subtotal"  : i.sub_total,
    } for i in cart_query]

    return [{
        "status" : 200,
        "message": "Data fetch successfully hx.",
        "item"   : {
            "cart_id"   : cart_query.cart_id,
            "updated_by": current_user.id,
            "updated_at": datetime.now(),
            "sub_item"  : sub_items
        }
    }]

  # @app.get("/cart_items/{id}", tags=["Cart"])
  # def cart(
  #     id : str,
  #     current_user : User = Depends(AdminPermission),
  #     db          : Session = Depends(get_db),
  # ):
  #     cart_query_id = db.query(TBL_CART).filter(TBL_CART.id == id).first()
  #     if not cart_query_id:
  #         return ("No record found with given id te.")
  #     return {
  #         "status"  : 200,
  #         "message" : "Data fetch successfully",
  #         "item"    : cart_query_id
  #     }

  # @app.put("/cart/{id}", tags=["Cart"])
  # def cart(
  #     id : str,
  #     current_user : User = Depends(AdminPermission),
  #     db          : Session = Depends(get_db),
  # ):
  #     cart_query_id = db.query(TBL_CART).filter(TBL_CART.id == id).first()
  #     if not cart_query_id:
  #         return ("No record found with given id te.")
    
  #     full_name = current_user.first_name + " " + current_user.last_name

  #     cart_query_id.user_id     = cart.user_id
  #     cart_query_id.total_price = cart.total_price
  #     cart_query_id.status      = cart.status
  #     updated_by                = full_name,
  #     updated_at                = datetime.now()
    
  #     db.commit()
  #     db.refresh(cart_query_id)
  #     return {
  #         "status"  : 200,
  #         "message" : "Data update successfully",
  #         "item"    : {
  #             "user_id"    : cart_query_id.user_id,
  #             "total_price": cart_query_id.total_price,
  #             "user_id"    : cart_query_id.status,
  #         }
  #     }

  # @app.delete("/cart/{id}", tags=["Cart"])
  # def cart(
  #     id : str,
  #     db          : Session = Depends(get_db),
  #     current_user : User = Depends(AdminPermission)
  # ):
  #     cart_query_id = db.query(TBL_CART).filter(TBL_CART.id == id).first()
  #     if not cart_query_id:
  #         return ("No record found with given id te.")
  #     db.delete(cart_query_id)
  #     db.commit()
  #     return {
  #         "status"  : 200,
  #         "message" : "Data deleted successfully"
  #     }


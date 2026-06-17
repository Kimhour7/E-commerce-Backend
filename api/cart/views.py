from fastapi import Depends

from core.custom_id import generate_prefixed_id
from core.db import get_db
from core.permission import AdminPermission
from core.securerity import User

from .schemas import *
from api.cart.models import TBL_CART
from main import app
from sqlalchemy.orm import Session
from datetime import datetime
# id = generate_prefixed_id(db=db, model=TBL_CART, prefix="CART")
@app.post("/cart/insert", tags=["Cart"])
def cart(
    cart: cartSchema,
    current_user: User = Depends(AdminPermission),
    db          : Session = Depends(get_db),
):
    new_cart = TBL_CART(
        id          = generate_prefixed_id(db=db, model=TBL_CART, prefix="CART"),
        user_id     = cart.user_id,
        total_price = cart.total_price,
        status      = cart.status,
        created_by  = current_user.id,
        updated_by  = current_user.id,
        created_at  = datetime.now(),
        updated_at  = datetime.now()
    )
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    return [{
        "status"  : 200,
        "message" : "Data insert successfully hx.",
        "item"    : {
            "user_id"    : cart.user_id,
            "total_price": cart.total_price,
            "user_id"    : cart.status,
        }
    }]

@app.get("/cart", tags=["Cart"])
def cart(
    current_user: User = Depends(AdminPermission),
    db          : Session = Depends(get_db),
):
    cart_query = db.query(TBL_CART).filter(TBL_CART.user_id == current_user.id).all()
    return [{
        "status"  : 200,
        "message" : "Data insert successfully hx.",
        "item"    : cart_query
    }]

@app.get("/cart/{id}", tags=["Cart"])
def cart(
    id : str,
    current_user : User = Depends(AdminPermission),
    db          : Session = Depends(get_db),
):
    cart_query_id = db.query(TBL_CART).filter(TBL_CART.user_id == current_user.id).filter(TBL_CART.id == id).first()
    if not cart_query_id:
        return ("No record found with given id te.")
    return {
        "status"  : 200,
        "message" : "Data fetch successfully",
        "item"    : cart_query_id
    }

@app.put("/cart/{id}", tags=["Cart"])
def cart(
    id : str,
    current_user : User = Depends(AdminPermission),
    db          : Session = Depends(get_db),
):
    cart_query_id = db.query(TBL_CART).filter(TBL_CART.id == id).first()
    if not cart_query_id:
        return ("No record found with given id te.")
    
    full_name = current_user.first_name + " " + current_user.last_name

    cart_query_id.user_id     = cart.user_id
    cart_query_id.total_price = cart.total_price
    cart_query_id.status      = cart.status
    updated_by                = full_name,
    updated_at                = datetime.now()
    
    db.commit()
    db.refresh(cart_query_id)
    return {
        "status"  : 200,
        "message" : "Data update successfully",
        "item"    : {
            "user_id"    : cart_query_id.user_id,
            "total_price": cart_query_id.total_price,
            "user_id"    : cart_query_id.status,
        }
    }

@app.delete("/cart/{id}", tags=["Cart"])
def cart(
    id : str,
    db          : Session = Depends(get_db),
    current_user : User = Depends(AdminPermission)
):
    cart_query_id = db.query(TBL_CART).filter(TBL_CART.id == id).first()
    if not cart_query_id:
        return ("No record found with given id te.")
    db.delete(cart_query_id)
    db.commit()
    return {
        "status"  : 200,
        "message" : "Data deleted successfully"
    }

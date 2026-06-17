from os import name

from fastapi import Depends
from sqlalchemy.orm import Session

from api.product_tag.models import TBL_PRODUCT_TAG
from api.product_tag.schemas import ProductTagSchemas
from core.custom_id import generate_prefixed_id
from core.db import get_db
from core.permission import AdminPermission
from core.photo_maker import get_username
from core.securerity import User
from main import app

@app.post("/product-tag", tags=["Product Tag"])
def product_tag_create(
    product_tag : ProductTagSchemas,
    db          : Session = Depends(get_db),
    current_user: User = Depends(AdminPermission),
):
    username   = get_username(current_user)

    product_tag = TBL_PRODUCT_TAG(    
        id          = generate_prefixed_id(db=db, model=TBL_PRODUCT_TAG, prefix="PRO-TAG"),
        name        = product_tag.name,
        created_by  = username,
        updated_by  = username,
    )

    db.add(product_tag)
    db.commit()
    db.refresh(product_tag)

    return {
        "success" : True,
        "message" : "Category created successfully",
        "data"    : product_tag,
    }
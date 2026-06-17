from typing import Optional

from fastapi import Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from api.sub_category.models import TBL_SUB_CATEGORY
from core.custom_id import generate_prefixed_id
from core.db import get_db
from core.permission import AdminPermission
from core.photo_maker import build_photo_url, get_username, save_file
from core.securerity import User
from main import app

UPLOAD_DIR = "static/uploads/sub-categories"

@app.post("/sub-category-create", tags=["Sub Category"])
def sub_category_create(
    category_id : str                   = Form(...),
    name        : str                   = Form(...),
    photo       : Optional[UploadFile]  = File(None),
    db          : Session               = Depends(get_db),
    current_user: User                  = Depends(AdminPermission),
):
    photo_path = save_file(photo, UPLOAD_DIR) if photo else None
    username   = get_username(current_user)

    sub_category = TBL_SUB_CATEGORY(    
        id          = generate_prefixed_id(db=db, model=TBL_SUB_CATEGORY, prefix="SUB-CAT"),
        category_id = category_id,
        name        = name,
        photo       = photo_path,
        created_by  = username,
        updated_by  = username,
    )

    db.add(sub_category)
    db.commit()
    db.refresh(sub_category)

    return {
        "success" : True,
        "message" : "Category created successfully",
        "data"    : sub_category,
        "photo_link": build_photo_url(sub_category.photo),
    }
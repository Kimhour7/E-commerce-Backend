import os
import shutil
from fastapi import Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional
from api.category.models import TBL_CATEGORY
from core.db import get_db
from core.permission import *
from core.photo_maker import build_photo_url, delete_file, get_username, save_file
from core.securerity import User, get_current_user
from core.custom_id import generate_prefixed_id
from main import website

UPLOAD_DIR = "static/uploads/categories"

@website.get("/get-category", tags=["Category"])
def get_all(
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
    page        : int     = 1,
    size        : int     = 10,
    search      : str     = None,
):
    query = db.query(TBL_CATEGORY)

    if search:
        query = query.filter(
            or_(
                TBL_CATEGORY.name.ilike(f"%{search}%"),
                TBL_CATEGORY.id.ilike(f"%{search}%"),
            )
        )

    all_results = query.all()

    data = []
    for row in all_results:
        item = {
            "id"         : row.id,
            "name"       : row.name,
            "photo"      : row.photo,
            "photo_link" : build_photo_url(row.photo),
            "created_by" : row.created_by,
            "updated_by" : row.updated_by,
            "created_at" : str(row.created_at) if row.created_at else None,
            "updated_at" : str(row.updated_at) if row.updated_at else None,
        }
        data.append(item)

    total_count    = len(data)
    start_idx      = (page - 1) * size
    paginated_data = data[start_idx : start_idx + size]

    return {
        "success"     : True,
        "message"     : "Categories retrieved successfully",
        "total"       : total_count,
        "page"        : page,
        "size"        : size,
        "total_pages" : (total_count + size - 1) // size,
        "data"        : paginated_data,
    }

@website.get("/category/{category_id}", tags=["Category"])
def get_by_id(
    category_id : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    category = db.query(TBL_CATEGORY).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return {
        "success"   : True,
        "message"   : "Category retrieved successfully",
        "data"      : category,
        "photo_link": build_photo_url(category.photo)
    }


@website.post("/category-create", tags=["Category"])
def create(
    name        : str                   = Form(...),
    photo       : Optional[UploadFile]  = File(None),
    db          : Session               = Depends(get_db),
    current_user: User                  = Depends(AdminPermission),
):
    
    photo_path = save_file(photo, UPLOAD_DIR) if photo else None
    username   = get_username(current_user)

    category = TBL_CATEGORY(
        id         = generate_prefixed_id(db=db, model=TBL_CATEGORY, prefix="CAT"),
        name       = name,
        photo      = photo_path,
        created_by = username,
        updated_by = username,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "success" : True,
        "message" : "Category created successfully",
        "data"    : category,
        "photo_link": build_photo_url(category.photo)
    }


@website.put("/category-update/{category_id}", tags=["Category"])
def update(
    category_id : str,
    name        : str                   = Form(...),
    photo       : Optional[UploadFile]  = File(None),
    db          : Session               = Depends(get_db),
    current_user: User                  = Depends(AdminPermission),
):
    category = db.query(TBL_CATEGORY).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name       = name
    category.updated_by = get_username(current_user)

    if photo:
        # Remove old file if it exists
        if category.photo and os.path.exists(category.photo):
            os.remove(category.photo)
        
        category.photo = save_file(photo, UPLOAD_DIR)

    db.commit()
    db.refresh(category)

    return {
        "success" : True,
        "message" : "Category updated successfully",
        "data"    : category,
        "photo_link": build_photo_url(category.photo)
    }


@website.delete("/category-delete/{category_id}", tags=["Category"])
def delete(
    category_id : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    category = db.query(TBL_CATEGORY).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.photo and os.path.exists(category.photo):
        delete_file(category.photo)

    db.delete(category)
    db.commit()

    return {
        "success" : True,
        "message" : f"Category {category_id} deleted successfully",
    }
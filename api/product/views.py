from typing import Optional
from fastapi import Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session
from api.category.models import TBL_CATEGORY
from api.product.models import TBL_PRODUCT
from api.product_tag.models import TBL_PRODUCT_TAG
from api.sub_category.models import TBL_SUB_CATEGORY
from core.custom_id import generate_prefixed_id
from core.db import get_db
from core.permission import AdminPermission
from core.photo_maker import build_photo_url, delete_file, get_username, save_file
from core.securerity import User, get_current_user
from main import app

UPLOAD_DIR = "static/uploads/products"

@app.post("/product-create", tags=["Product"])
def create(
    category_id     : str                  = Form(...),
    sub_category_id : str                  = Form(...),
    product_tag_id  : str                  = Form(...),
    name            : str                  = Form(...),
    stock           : int                  = Form(...),
    price           : float                = Form(...),
    description     : str                  = Form(None),
    photo           : Optional[UploadFile] = File(None),
    db              : Session              = Depends(get_db),
    current_user   : User                  = Depends(AdminPermission),
):
    try:
        photo_path = save_file(photo, UPLOAD_DIR) if photo else None
        username   = get_username(current_user)

        get_category = (
            db.query(TBL_CATEGORY)
            .filter(TBL_CATEGORY.id == category_id)
            .first()
        )

        if not get_category:
            raise HTTPException(status_code=404, detail="Category not found.")
        
        get_sub_category = (
            db.query(TBL_SUB_CATEGORY)
            .filter(TBL_SUB_CATEGORY.id == sub_category_id)
            .first()
        )

        if not get_sub_category:
            raise HTTPException(status_code=404, detail="Sub Category not found.")
        
        get_product_tag_id = (
            db.query(TBL_PRODUCT_TAG)
            .filter(TBL_PRODUCT_TAG.id == product_tag_id)
            .first()
        )

        if not get_product_tag_id:
            raise HTTPException(status_code=404, detail="Product Tag not found.")

        product = TBL_PRODUCT(
            id              = generate_prefixed_id(db=db, model=TBL_PRODUCT, prefix="PRO"),
            category_id     = get_category.id,
            sub_category_id = get_sub_category.id,
            product_tag_id  = get_product_tag_id.id,
            name            = name,
            stock           = stock,
            price           = price,
            description     = description,
            photo           = photo_path,
            created_by      = username,
            updated_by      = username,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return {
            "success" : True,
            "message" : "Category created successfully",
            "data"    : product,
            "photo_link": build_photo_url(product.photo)
        }
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "success": False,
            "message" : str(e),
            "error": traceback.format_exc()
        }
    
@app.get("/get-product", tags=["Product"])
def get_all(
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
    page        : int     = 1,
    size        : int     = 10,
    search      : str     = None,
    filter      : str     = None,
):
    query = db.query(TBL_PRODUCT)

    if filter:
        query = query.filter(
            TBL_PRODUCT.category_id == filter
        )

    if search:
        query = query.filter(
            or_(
                TBL_PRODUCT.name.ilike(f"%{search}%"),
                TBL_PRODUCT.id.ilike(f"%{search}%"),
            )
        )

    all_results = query.all()

    data = []
    for row in all_results:
        item = {
            "id"         : row.id,
            "category_id": row.category_id,
            "sub_category_id": row.sub_category_id,
            "product_tag_id": row.product_tag_id,
            "name"       : row.name,
            "stock"      : row.stock,
            "price"      : row.price,
            "active"     : row.active,
            "description": row.description if row.description else None,
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

@app.put("/product-update/{product_id}", tags=["Product"])
def update(
    product_id  : str,
    category_id : str                   = Form(...),
    name        : str                   = Form(...),
    stock       : int                   = Form(...),
    price       : float                 = Form(...),
    description : str                   = Form(None),
    photo       : Optional[UploadFile]  = File(None),
    db          : Session               = Depends(get_db),
    current_user: User                  = Depends(AdminPermission),
):
    try:
        product = db.query(TBL_PRODUCT).filter_by(id=product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        get_category = db.query(TBL_CATEGORY).filter(TBL_CATEGORY.id == category_id).first()
        if not get_category:
            raise HTTPException(status_code=404, detail="Category not found.")

        product.category_id = get_category.id
        product.name        = name
        product.stock       = stock
        product.price       = price
        product.description = description
        product.updated_by  = get_username(current_user)

        if photo:
            delete_file(product.photo)
            product.photo = save_file(photo, UPLOAD_DIR)  

        db.commit()
        db.refresh(product)

        return {
            "success"    : True,
            "message"    : "Product updated successfully",
            "data"       : product,
            "photo_link" : build_photo_url(product.photo),
        }
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "success" : False,
            "message" : str(e),
            "error"   : traceback.format_exc(),
        }


@app.delete("/product-delete/{product_id}", tags=["Product"])
def delete(
    product_id  : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    try:
        product = db.query(TBL_PRODUCT).filter_by(id=product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        delete_file(product.photo)

        db.delete(product)
        db.commit()

        return {
            "success" : True,
            "message" : f"Product {product_id} deleted successfully",
        }
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "success" : False,
            "message" : str(e),
            "error"   : traceback.format_exc(),
        }
    
@app.get("/product/{product_id}", tags=["Product"])
def get_by_id(
    product_id : str,
    db          : Session = Depends(get_db),
):
    get_product = db.query(TBL_PRODUCT).filter(TBL_PRODUCT.id == product_id).first()

    if not get_product:
        return HTTPException(status_code=404, detail="Product not found.")

    return {
        "success"    : True,
        "message"    : "Product retrieved successfully",
        "data"       : get_product,
    }
from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api.category.models import TBL_CATEGORY
from api.product.models import TBL_PRODUCT
from core.db import get_db
from core.photo_maker import build_photo_url
from main import website

@website.get("/list-product-category", tags=["Frontend"])
def get_list_product(
    db          : Session = Depends(get_db),
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

@website.get("/get-list-product-by-category", tags=["Frontend"])
def get_list_product(
    db          : Session = Depends(get_db),
    page        : int     = 1,
    size        : int     = 10,
    search      : str     = None
):
    query = db.query(TBL_CATEGORY)
    
    all_results = query.all()

    data = []
    for row in all_results:
        product_data = []

        all_product = db.query(TBL_PRODUCT).filter(TBL_PRODUCT.category_id == row.id).limit(5)
        
        for product_row in all_product:
            product_item = {
                "id"         : product_row.id,
                "name"       : product_row.name,
                "stock"      : product_row.stock,
                "price"      : product_row.price,
                "description": product_row.description,
                "photo"      : product_row.photo,
                "photo_link" : build_photo_url(product_row.photo),
                "created_by" : product_row.created_by,
                "updated_by" : product_row.updated_by,
                "created_at" : product_row.created_at,
                "updated_at" : product_row.updated_at,
            }
            product_data.append(product_item)

        item = {
            "id"         : row.id,
            "name"       : row.name,
            "photo"      : row.photo,
            "product"    : product_data,
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
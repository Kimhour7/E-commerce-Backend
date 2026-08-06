from fastapi import Depends, File, Form, UploadFile

from core.permission import UserPermission
from core.securerity import User
from main import website
from api.upload.image.service import (
    build_upload_response,
    delete_cloudinary_image,
    upload_cloudinary_image,
)


@website.post("/upload-image", tags=["Upload"])
def upload_image(
    image: UploadFile = File(...),
    current_user: User = Depends(UserPermission),
):
    result = upload_cloudinary_image(image)
    return build_upload_response(result)


@website.put("/update-image", tags=["Upload"])
def update_image(
    public_id: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(UserPermission),
):
    result = upload_cloudinary_image(
        image=image,
        public_id=public_id,
        overwrite=True,
    )
    return build_upload_response(result)


@website.delete("/delete-image", tags=["Upload"])
def delete_image(
    public_id: str,
    current_user: User = Depends(UserPermission),
):
    result = delete_cloudinary_image(public_id)

    return {
        "success": True,
        "message": "Image deleted successfully",
        "data": result,
    }

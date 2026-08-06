from typing import Any
from urllib.parse import unquote, urlparse

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from config import configs

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def configure_cloudinary() -> None:
    if not all([
        configs.CLOUDINARY_CLOUD_NAME,
        configs.CLOUDINARY_API_KEY,
        configs.CLOUDINARY_API_SECRET,
    ]):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary configuration is missing",
        )

    cloudinary.config(
        cloud_name=configs.CLOUDINARY_CLOUD_NAME,
        api_key=configs.CLOUDINARY_API_KEY,
        api_secret=configs.CLOUDINARY_API_SECRET,
        secure=True,
    )


def build_upload_response(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": True,
        "message": "Image uploaded successfully",
        "data": {
            "public_id": result.get("public_id"),
            "url": result.get("secure_url") or result.get("url"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "bytes": result.get("bytes"),
            "resource_type": result.get("resource_type"),
        },
    }


def get_cloudinary_public_id(image_ref: str | None) -> str | None:
    if not image_ref:
        return None

    if not image_ref.startswith(("http://", "https://")):
        return image_ref

    parsed_url = urlparse(image_ref)
    path_parts = [part for part in parsed_url.path.split("/") if part]
    upload_index = path_parts.index("upload") if "upload" in path_parts else -1

    if upload_index == -1:
        return None

    public_id_parts = path_parts[upload_index + 1 :]
    if public_id_parts and public_id_parts[0].startswith("v") and public_id_parts[0][1:].isdigit():
        public_id_parts = public_id_parts[1:]

    if not public_id_parts:
        return None

    public_id = "/".join(public_id_parts)
    if "." in public_id:
        public_id = public_id.rsplit(".", 1)[0]

    return public_id


def upload_cloudinary_image(
    image: UploadFile,
    folder: str | None = None,
    public_id: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpeg, png, webp, and gif image files are allowed",
        )

    configure_cloudinary()

    upload_options: dict[str, Any] = {
        "folder": folder or configs.CLOUDINARY_FOLDER,
        "resource_type": "image",
    }

    if overwrite:
        upload_options["overwrite"] = True
        upload_options["invalidate"] = True

    if public_id:
        upload_options["public_id"] = get_cloudinary_public_id(public_id)

    try:
        return cloudinary.uploader.upload(image.file, **upload_options)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cloudinary upload failed: {str(exc)}",
        ) from exc


def delete_cloudinary_image(image_ref: str | None) -> dict[str, Any] | None:
    public_id = get_cloudinary_public_id(image_ref)
    if not public_id:
        return None

    configure_cloudinary()

    try:
        return cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            invalidate=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cloudinary delete failed: {str(exc)}",
        ) from exc

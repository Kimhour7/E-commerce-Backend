import os
import shutil
from fastapi import UploadFile
from fastapi.staticfiles import StaticFiles

from config import configs
from core.securerity import User
from main import app

# ── Static mount (once for the whole app) ────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_photo_url(photo_path: str | None) -> str | None:
    """Convert a local file-system path to a full browser-accessible URL."""
    if not photo_path:
        return None
    relative = photo_path.replace("\\", "/").lstrip("/")
    return f"{configs.APP_URL}/{relative}"


def get_username(current_user: User) -> str:
    """Return a display name from the current user."""
    username = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
    return username or current_user.username


def save_file(photo: UploadFile, upload_dir: str) -> str:
    """
    Persist an uploaded file into `upload_dir` and return its local path.

    Usage:
        path = save_file(photo, "static/uploads/categories")
        path = save_file(photo, "static/uploads/products")
    """
    os.makedirs(upload_dir, exist_ok=True)
    filename   = f"{os.urandom(8).hex()}_{photo.filename}"
    photo_path = f"{upload_dir}/{filename}"
    with open(photo_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    return photo_path


def delete_file(file_path: str | None) -> None:
    """Safely delete a file from the filesystem if it exists."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
import os
import uuid

from werkzeug.utils import secure_filename

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
CHAT_EXTENSIONS = {
    "png", "jpg", "jpeg", "webp", "gif", "pdf", "txt", "csv",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx", "zip",
    "mp3", "wav", "m4a", "ogg", "webm",
}


def allowed_file(filename, allowed_extensions=IMAGE_EXTENSIONS):
    return bool(filename and "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions)


def save_upload(file, upload_folder, allowed_extensions=IMAGE_EXTENSIONS):
    if not file or not allowed_file(file.filename, allowed_extensions):
        return None

    safe_name = secure_filename(file.filename)
    if not safe_name:
        return None

    extension = safe_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, filename)
    file.save(path)
    return filename, safe_name, os.path.getsize(path)


def save_image(file, upload_folder):
    saved = save_upload(file, upload_folder, IMAGE_EXTENSIONS)
    return saved[0] if saved else None

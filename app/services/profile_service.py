import os

from flask import current_app

from app.extensions import db
from app.utils.file_handler import allowed_file, save_image


class ProfileService:

    @staticmethod
    def update_profile(user, form_data):

        user.bio = form_data.get("bio", "").strip()
        user.location = form_data.get("location", "").strip()
        user.website = form_data.get("website", "").strip()

        db.session.commit()

    @staticmethod
    def update_avatar(user, file):

        if not file or file.filename == "":
            return False

        if not allowed_file(file.filename):
            return False

        filename = save_image(
            file,
            current_app.config["UPLOAD_FOLDER"]
        )

        if not filename:
            return False

        current_avatar = getattr(user, "avatar", None) or ""

        if current_avatar and current_avatar != "default-avatar.png":
            old_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                current_avatar
            )

            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        user.avatar = filename

        db.session.commit()

        return True
import os
from datetime import datetime, timedelta

from flask import Blueprint, abort, current_app, jsonify, render_template, request, send_from_directory
from flask_login import current_user, login_required
from flask_socketio import emit

from app.extensions import socketio
from app.models.message import Message
from app.models.user import User
from app.services.chat_service import ChatService
from app.utils.file_handler import CHAT_EXTENSIONS, save_upload

chat = Blueprint("chat", __name__, url_prefix="/chat")


@chat.route("/")
@login_required
def chat_list():
    recent_messages = Message.query.filter((Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)).order_by(Message.created_at.desc()).all()
    chats, seen_users = [], set()
    for message in recent_messages:
        friend = message.receiver if message.sender_id == current_user.id else message.sender
        if friend.id in seen_users or not ChatService.can_chat(current_user.id, friend.id):
            continue
        seen_users.add(friend.id)
        chats.append({"user": friend, "last_message": message, "prefix": "You: " if message.sender_id == current_user.id else "", "unread_count": ChatService.unread_count(current_user.id, friend.id)})
    return render_template("chat/chat_list.html", chats=chats)


@chat.route("/<int:user_id>")
@login_required
def conversation(user_id):
    friend = User.query.get_or_404(user_id)
    friend_is_online = bool(friend.is_online and (friend.last_seen is None or friend.last_seen >= datetime.utcnow() - timedelta(minutes=2)))
    if not ChatService.can_chat(current_user.id, friend.id):
        return render_template("chat/conversation.html", friend=friend, friend_is_online=friend_is_online, messages=[], chat_unavailable=True), 403
    return render_template("chat/conversation.html", friend=friend, friend_is_online=friend_is_online, messages=ChatService.get_conversation(current_user.id, friend.id), chat_unavailable=False)


@chat.route("/attachments/<int:message_id>")
@login_required
def download_attachment(message_id):
    message = Message.query.get_or_404(message_id)
    if not message.attachment_path or current_user.id not in (message.sender_id, message.receiver_id):
        abort(404)
    if not ChatService.can_chat(current_user.id, message.receiver_id if message.sender_id == current_user.id else message.sender_id):
        abort(403)
    return send_from_directory(current_app.config["CHAT_UPLOAD_FOLDER"], message.attachment_path, download_name=message.attachment_name)


@chat.route("/<int:user_id>/attachments", methods=["POST"])
@login_required
def upload_attachment(user_id):
    if not ChatService.can_chat(current_user.id, user_id):
        return jsonify(error="You can only share files with accepted friends."), 403
    uploaded_file = request.files.get("file")
    saved = save_upload(uploaded_file, current_app.config["CHAT_UPLOAD_FOLDER"], CHAT_EXTENSIONS)
    if not saved:
        return jsonify(error="Unsupported or empty file."), 400
    filename, original_name, size = saved
    mime = uploaded_file.mimetype or "application/octet-stream"
    attachment_type = "voice" if mime.startswith("audio/") else ("image" if mime.startswith("image/") else "file")
    message = ChatService.send_message(current_user, user_id, request.form.get("caption", ""), {"path": filename, "name": original_name, "mime": mime, "size": size, "type": attachment_type})
    if not message:
        os.remove(os.path.join(current_app.config["CHAT_UPLOAD_FOLDER"], filename))
        return jsonify(error="Could not send attachment."), 400
    payload = ChatService.serialize_message(message)
    socketio.emit("receive_message", payload, room=f"user_{current_user.id}")
    socketio.emit("receive_message", payload, room=f"user_{user_id}")
    return jsonify(payload), 201

from datetime import datetime

from flask_login import current_user
from flask_socketio import emit, join_room

from app.extensions import db, socketio
from app.services.chat_service import ChatService


def _friend_room(friend_id):
    try:
        friend_id = int(friend_id)
    except (TypeError, ValueError):
        return None
    if not current_user.is_authenticated or not ChatService.can_chat(current_user.id, friend_id):
        return None
    return ChatService.room_name(current_user.id, friend_id)


@socketio.on("connect")
def handle_connect():
    if not current_user.is_authenticated:
        return False
    current_user.is_online = True
    db.session.commit()
    join_room(f"user_{current_user.id}")
    emit("user_online", {"user_id": current_user.id}, broadcast=True, include_self=False)


@socketio.on("disconnect")
def handle_disconnect():
    if not current_user.is_authenticated:
        return
    current_user.is_online = False
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    emit("user_offline", {"user_id": current_user.id, "last_seen": ChatService.format_time(current_user.last_seen)}, broadcast=True, include_self=False)


@socketio.on("join")
def handle_join(data):
    friend_id = (data or {}).get("friend_id")
    if friend_id is None:
        return
    room = _friend_room(friend_id)
    if not room:
        emit("chat_error", {"message": "You do not have access to this conversation."})
        return
    join_room(room)
    emit("chat_joined", {"room": room})


@socketio.on("send_message")
def handle_send_message(data):
    data = data or {}
    receiver_id = data.get("receiver_id")
    room = _friend_room(receiver_id)
    if not room:
        emit("chat_error", {"message": "You can only message accepted friends."})
        return
    message = ChatService.send_message(current_user, receiver_id, data.get("message"))
    if not message:
        emit("chat_error", {"message": "Message must contain 1 to 4,000 characters."})
        return
    payload = ChatService.serialize_message(message)
    emit("receive_message", payload, room=f"user_{current_user.id}")
    emit("receive_message", payload, room=f"user_{receiver_id}")


@socketio.on("conversation_opened")
def handle_conversation_opened(data):
    friend_id = (data or {}).get("friend_id")
    room = _friend_room(friend_id)
    if not room:
        return
    read_ids = ChatService.mark_messages_as_read(current_user.id, friend_id)
    if read_ids:
        emit("messages_read", {"message_ids": read_ids}, room=f"user_{friend_id}")


@socketio.on("typing")
def handle_typing(data):
    room = _friend_room((data or {}).get("friend_id"))
    if room:
        emit("show_typing", {"user_id": current_user.id, "username": current_user.username}, room=room, include_self=False)


@socketio.on("stop_typing")
def handle_stop_typing(data):
    room = _friend_room((data or {}).get("friend_id"))
    if room:
        emit("hide_typing", {"user_id": current_user.id}, room=room, include_self=False)

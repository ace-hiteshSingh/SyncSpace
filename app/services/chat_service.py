from datetime import datetime

from app.extensions import db
from app.models.message import Message
from app.models.user import User
from app.services.friend_service import FriendService


class ChatService:
    MAX_MESSAGE_LENGTH = 4000

    @staticmethod
    def room_name(user_id, friend_id):
        return f"chat_{min(int(user_id), int(friend_id))}_{max(int(user_id), int(friend_id))}"

    @staticmethod
    def can_chat(user_id, friend_id):
        return user_id != friend_id and User.query.get(friend_id) is not None and FriendService.are_friends(user_id, friend_id)

    @staticmethod
    def send_message(sender, receiver_id, content="", attachment=None):
        try:
            receiver_id = int(receiver_id)
        except (TypeError, ValueError):
            return None
        if not ChatService.can_chat(sender.id, receiver_id):
            return None

        content = (content or "").strip()
        if len(content) > ChatService.MAX_MESSAGE_LENGTH or (not content and not attachment):
            return None

        message = Message(sender_id=sender.id, receiver_id=receiver_id, content=content, is_read=False)
        if attachment:
            message.attachment_path = attachment["path"]
            message.attachment_name = attachment["name"]
            message.attachment_mime = attachment["mime"]
            message.attachment_size = attachment["size"]
            message.attachment_type = attachment["type"]
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def serialize_message(message):
        return {
            "id": message.id, "sender_id": message.sender_id, "receiver_id": message.receiver_id,
            "sender_name": message.sender.username, "receiver_name": message.receiver.username,
            "message": message.content, "time": message.created_at.strftime("%I:%M %p"),
            "is_read": message.is_read,
            "attachment": ({"url": f"/chat/attachments/{message.id}", "name": message.attachment_name,
                            "mime": message.attachment_mime, "size": message.attachment_size,
                            "type": message.attachment_type} if message.attachment_path else None),
        }

    @staticmethod
    def get_conversation(user1_id, user2_id):
        if not ChatService.can_chat(user1_id, user2_id):
            return []
        return Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.created_at.asc()).all()

    @staticmethod
    def last_message(user1_id, user2_id):
        return Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.created_at.desc()).first()

    @staticmethod
    def mark_messages_as_read(receiver_id, sender_id):
        if not ChatService.can_chat(receiver_id, sender_id):
            return []
        unread_messages = Message.query.filter(
            Message.sender_id == sender_id, Message.receiver_id == receiver_id, Message.is_read.is_(False)
        ).all()
        now = datetime.utcnow()
        for message in unread_messages:
            message.is_read, message.read_at = True, now
        db.session.commit()
        return [message.id for message in unread_messages]

    @staticmethod
    def unread_count(receiver_id, sender_id):
        return Message.query.filter(Message.sender_id == sender_id, Message.receiver_id == receiver_id, Message.is_read.is_(False)).count()

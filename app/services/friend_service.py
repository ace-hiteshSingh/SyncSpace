from app.extensions import db
from app.models.user import User
from app.models.friend import Friend


class FriendService:

    @staticmethod
    def are_friends(user_id, other_user_id):
        return Friend.query.filter(
            (((Friend.sender_id == user_id) & (Friend.receiver_id == other_user_id)) |
             ((Friend.sender_id == other_user_id) & (Friend.receiver_id == user_id))),
            Friend.status == "accepted"
        ).first() is not None

    @staticmethod
    def search_users(current_user, query):

        if not query:
            return []

        users = User.query.filter(
            User.username.ilike(f"%{query}%"),
            User.id != current_user.id
        ).all()

        return users

    @staticmethod
    def send_request(sender, receiver_id):

        if sender.id == receiver_id:
            return False, "You cannot send a friend request to yourself."

        existing = Friend.query.filter(
            (
                (Friend.sender_id == sender.id) &
                (Friend.receiver_id == receiver_id)
            ) |
            (
                (Friend.sender_id == receiver_id) &
                (Friend.receiver_id == sender.id)
            )
        ).first()

        if existing:
            return False, "Friend request already exists."

        friend = Friend(
            sender_id=sender.id,
            receiver_id=receiver_id,
            status="pending"
        )

        db.session.add(friend)
        db.session.commit()

        return True, "Friend request sent successfully!"

    @staticmethod
    def incoming_requests(user):

        return Friend.query.filter_by(
            receiver_id=user.id,
            status="pending"
        ).all()

    @staticmethod
    def accept_request(request_id, receiver_id):

        friend = Friend.query.get(request_id)

        if not friend or friend.receiver_id != receiver_id or friend.status != "pending":
            return False

        friend.status = "accepted"

        db.session.commit()

        return True

    @staticmethod
    def reject_request(request_id, receiver_id):

        friend = Friend.query.get(request_id)

        if not friend or friend.receiver_id != receiver_id or friend.status != "pending":
            return False

        db.session.delete(friend)

        db.session.commit()

        return True

    @staticmethod
    def friends_list(user):

        friendships = Friend.query.filter(
            (
                (Friend.sender_id == user.id) |
                (Friend.receiver_id == user.id)
            ) &
            (Friend.status == "accepted")
        ).all()

        friends = []

        for friendship in friendships:

            if friendship.sender_id == user.id:
                friends.append(friendship.receiver)
            else:
                friends.append(friendship.sender)

        return friends

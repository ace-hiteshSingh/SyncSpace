from datetime import datetime

from app.extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    attachment_path = db.Column(db.String(255), nullable=True)
    attachment_name = db.Column(db.String(255), nullable=True)
    attachment_mime = db.Column(db.String(100), nullable=True)
    attachment_size = db.Column(db.Integer, nullable=True)
    attachment_type = db.Column(db.String(20), nullable=True)

    # ==========================
    # Read Status
    # ==========================

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    read_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ==========================
    # Timestamps
    # ==========================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ==========================
    # Relationships
    # ==========================

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id]
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id]
    )

    def mark_as_read(self):
        """
        Mark the message as read.
        """

        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()

    def __repr__(self):
        return (
            f"<Message "
            f"id={self.id} "
            f"from={self.sender_id} "
            f"to={self.receiver_id} "
            f"read={self.is_read}>"
        )

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    # NEW: Admin role
    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    files = db.relationship(
        "File",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )


class File(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    encrypted_filename = db.Column(
        db.String(255),
        nullable=False
    )

    filesize = db.Column(
        db.Float,
        default=0
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    downloads = db.Column(
        db.Integer,
        default=0
    )

    favorite = db.Column(
        db.Boolean,
        default=False
    )

    shared = db.Column(
        db.Boolean,
        default=False
    )

    share_token = db.Column(
        db.String(120),
        unique=True,
        nullable=True
    )

    expiry_date = db.Column(
        db.DateTime,
        nullable=True
    )

    share_password = db.Column(
        db.String(255),
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    
from flask_sqlalchemy import SQLAlchemy
from pgvector.sqlalchemy import Vector
from datetime import datetime

db = SQLAlchemy()

class VectorEmbedding(db.Model):
    __tablename__ = 'vector_embeddings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(255), nullable=False)  # User ID
    mongo_doc_id = db.Column(db.String(255), nullable=False, unique=True)  # MongoDB document ID
    embedding = db.Column(Vector(1024), nullable=False)  # Vector embedding
    content_type = db.Column(db.String(50), nullable=False)  # Content type (e.g., blog, presentation)
    additional_info = db.Column(db.String(255), nullable=True)  # Additional contextual info
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)  # Timestamp

    actions = db.relationship("ActionLog", back_populates="embedding", cascade="all, delete-orphan")


class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    embedding_id = db.Column(db.Integer, db.ForeignKey('vector_embeddings.id'), nullable=False)  # FK to VectorEmbedding
    action_type = db.Column(db.String(255), nullable=False)  # Action type (e.g., generated, updated, deleted)
    details = db.Column(db.String(255), nullable=True)  # Additional action details
    timestamp = db.Column(db.DateTime, default=datetime.now(), nullable=False)  # Action timestamp

    embedding = db.relationship("VectorEmbedding", back_populates="actions")

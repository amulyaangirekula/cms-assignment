import uuid
from datetime import datetime
from db import db

# Program table
class Program(db.Model):
    __tablename__ = "programs"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    language_primary = db.Column(db.String, nullable=False)
    languages_available = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String, default="draft")  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Topic table
class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, unique=True, nullable=False)


# Program-Topic (many-to-many)
class ProgramTopic(db.Model):
    __tablename__ = "program_topics"

    program_id = db.Column(db.String, db.ForeignKey("programs.id"), primary_key=True)
    topic_id = db.Column(db.String, db.ForeignKey("topics.id"), primary_key=True)


# Term table
class Term(db.Model):
    __tablename__ = "terms"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = db.Column(db.String, db.ForeignKey("programs.id"), nullable=False)
    term_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('program_id', 'term_number', name='uq_program_term'),
    )


# Lesson table
class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    term_id = db.Column(db.String, db.ForeignKey("terms.id"), nullable=False)
    lesson_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    content_type = db.Column(db.String, nullable=False)  # video, article
    duration_ms = db.Column(db.Integer)
    is_paid = db.Column(db.Boolean, default=False)

    content_language_primary = db.Column(db.String, nullable=False)
    content_languages_available = db.Column(db.JSON, nullable=False)
    content_urls_by_language = db.Column(db.JSON, nullable=False)

    subtitle_languages = db.Column(db.JSON)
    subtitle_urls_by_language = db.Column(db.JSON)

    status = db.Column(db.String, default="draft")  # draft, scheduled, published, archived
    publish_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('term_id', 'lesson_number', name='uq_term_lesson'),
    )

class ProgramAsset(db.Model):
    __tablename__ = "program_assets"

    id = db.Column(db.String, primary_key=True)
    program_id = db.Column(db.String, db.ForeignKey("programs.id"), nullable=False)
    language = db.Column(db.String, nullable=False)
    variant = db.Column(db.String, nullable=False)  # portrait | landscape | square | banner
    asset_type = db.Column(db.String, nullable=False)  # poster
    url = db.Column(db.String, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("program_id", "language", "variant", "asset_type", name="uniq_program_asset"),
    )


class LessonAsset(db.Model):
    __tablename__ = "lesson_assets"

    id = db.Column(db.String, primary_key=True)
    lesson_id = db.Column(db.String, db.ForeignKey("lessons.id"), nullable=False)
    language = db.Column(db.String, nullable=False)
    variant = db.Column(db.String, nullable=False)  # portrait | landscape | square | banner
    asset_type = db.Column(db.String, nullable=False)  # thumbnail
    url = db.Column(db.String, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("lesson_id", "language", "variant", "asset_type", name="uniq_lesson_asset"),
    )

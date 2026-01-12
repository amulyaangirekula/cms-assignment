from app import app
from db import db
from models import Program, Term, Lesson, ProgramAsset, LessonAsset
from datetime import datetime, timedelta
import uuid

def seed():
    with app.app_context():
        print("🌱 Seeding database...")

        # Clear existing data (order matters due to FKs)
        LessonAsset.query.delete()
        ProgramAsset.query.delete()
        Lesson.query.delete()
        Term.query.delete()
        Program.query.delete()
        db.session.commit()

        # ------------------
        # PROGRAM 1 (EN)
        # ------------------
        program1 = Program(
            id=str(uuid.uuid4()),
            title="Python Basics",
            description="Learn Python from scratch",
            language_primary="en",
            languages_available=["en"],
            status="draft"
        )
        db.session.add(program1)

        term1 = Term(
            id=str(uuid.uuid4()),
            program_id=program1.id,
            term_number=1,
            title="Introduction"
        )
        db.session.add(term1)

        # 🔑 COMMIT programs & terms FIRST
        db.session.commit()

        # Lessons for Program 1
        lesson1 = Lesson(
            id=str(uuid.uuid4()),
            term_id=term1.id,
            lesson_number=1,
            title="What is Python?",
            content_type="video",
            duration_ms=300000,
            is_paid=False,
            content_language_primary="en",
            content_languages_available=["en"],
            content_urls_by_language={"en": "https://example.com/python1"},
            status="published",
            published_at=datetime.utcnow()
        )

        lesson2 = Lesson(
            id=str(uuid.uuid4()),
            term_id=term1.id,
            lesson_number=2,
            title="Variables & Types",
            content_type="video",
            duration_ms=420000,
            is_paid=False,
            content_language_primary="en",
            content_languages_available=["en"],
            content_urls_by_language={"en": "https://example.com/python2"},
            status="published",
            published_at=datetime.utcnow()
        )

        # Scheduled lesson (auto publish demo)
        lesson3 = Lesson(
            id=str(uuid.uuid4()),
            term_id=term1.id,
            lesson_number=3,
            title="Control Flow",
            content_type="video",
            duration_ms=480000,
            is_paid=True,
            content_language_primary="en",
            content_languages_available=["en"],
            content_urls_by_language={"en": "https://example.com/python3"},
            status="scheduled",
            publish_at=datetime.utcnow() + timedelta(minutes=2)
        )

        db.session.add_all([lesson1, lesson2, lesson3])
        db.session.commit()

        # Program 1 posters
        poster1 = ProgramAsset(
            id=str(uuid.uuid4()),
            program_id=program1.id,
            language="en",
            variant="portrait",
            asset_type="poster",
            url="https://example.com/poster1_portrait.jpg"
        )
        poster2 = ProgramAsset(
            id=str(uuid.uuid4()),
            program_id=program1.id,
            language="en",
            variant="landscape",
            asset_type="poster",
            url="https://example.com/poster1_landscape.jpg"
        )

        db.session.add_all([poster1, poster2])

        # Lesson thumbnails
        for lesson in [lesson1, lesson2, lesson3]:
            thumb1 = LessonAsset(
                id=str(uuid.uuid4()),
                lesson_id=lesson.id,
                language="en",
                variant="portrait",
                asset_type="thumbnail",
                url="https://example.com/thumb_portrait.jpg"
            )
            thumb2 = LessonAsset(
                id=str(uuid.uuid4()),
                lesson_id=lesson.id,
                language="en",
                variant="landscape",
                asset_type="thumbnail",
                url="https://example.com/thumb_landscape.jpg"
            )
            db.session.add_all([thumb1, thumb2])

        db.session.commit()

        # ------------------
        # PROGRAM 2 (MULTI-LANGUAGE)
        # ------------------
        program2 = Program(
            id=str(uuid.uuid4()),
            title="AI for Beginners",
            description="Intro to AI concepts",
            language_primary="en",
            languages_available=["en", "hi"],
            status="draft"
        )
        db.session.add(program2)

        term2 = Term(
            id=str(uuid.uuid4()),
            program_id=program2.id,
            term_number=1,
            title="Getting Started"
        )
        db.session.add(term2)

        # 🔑 COMMIT programs & terms FIRST
        db.session.commit()

        lesson4 = Lesson(
            id=str(uuid.uuid4()),
            term_id=term2.id,
            lesson_number=1,
            title="What is AI?",
            content_type="article",
            is_paid=False,
            content_language_primary="en",
            content_languages_available=["en", "hi"],
            content_urls_by_language={
                "en": "https://example.com/ai_en",
                "hi": "https://example.com/ai_hi"
            },
            status="published",
            published_at=datetime.utcnow()
        )

        lesson5 = Lesson(
            id=str(uuid.uuid4()),
            term_id=term2.id,
            lesson_number=2,
            title="AI in Real Life",
            content_type="video",
            duration_ms=360000,
            is_paid=False,
            content_language_primary="en",
            content_languages_available=["en"],
            content_urls_by_language={"en": "https://example.com/ai2"},
            status="published",
            published_at=datetime.utcnow()
        )

        lesson6 = Lesson(
            id=str(uuid.uuid4()),
            term_id=term2.id,
            lesson_number=3,
            title="Future of AI",
            content_type="video",
            duration_ms=390000,
            is_paid=True,
            content_language_primary="en",
            content_languages_available=["en"],
            content_urls_by_language={"en": "https://example.com/ai3"},
            status="published",
            published_at=datetime.utcnow()
        )

        db.session.add_all([lesson4, lesson5, lesson6])
        db.session.commit()

        # Program 2 posters
        poster3 = ProgramAsset(
            id=str(uuid.uuid4()),
            program_id=program2.id,
            language="en",
            variant="portrait",
            asset_type="poster",
            url="https://example.com/poster2_portrait.jpg"
        )
        poster4 = ProgramAsset(
            id=str(uuid.uuid4()),
            program_id=program2.id,
            language="en",
            variant="landscape",
            asset_type="poster",
            url="https://example.com/poster2_landscape.jpg"
        )

        db.session.add_all([poster3, poster4])

        # Lesson thumbnails for program 2
        for lesson in [lesson4, lesson5, lesson6]:
            thumb1 = LessonAsset(
                id=str(uuid.uuid4()),
                lesson_id=lesson.id,
                language="en",
                variant="portrait",
                asset_type="thumbnail",
                url="https://example.com/thumb2_portrait.jpg"
            )
            thumb2 = LessonAsset(
                id=str(uuid.uuid4()),
                lesson_id=lesson.id,
                language="en",
                variant="landscape",
                asset_type="thumbnail",
                url="https://example.com/thumb2_landscape.jpg"
            )
            db.session.add_all([thumb1, thumb2])

        db.session.commit()
        print("✅ Seeding complete!")

if __name__ == "__main__":
    seed()

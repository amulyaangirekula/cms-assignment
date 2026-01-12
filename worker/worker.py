import time
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# Must match docker compose DB host name
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------
# MODELS
# -------------------

class Program(db.Model):
    __tablename__ = "programs"
    id = db.Column(db.String, primary_key=True)
    status = db.Column(db.String)
    published_at = db.Column(db.DateTime)


class Lesson(db.Model):
    __tablename__ = "lessons"
    id = db.Column(db.String, primary_key=True)
    term_id = db.Column(db.String)
    status = db.Column(db.String)
    publish_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)


class Term(db.Model):
    __tablename__ = "terms"
    id = db.Column(db.String, primary_key=True)
    program_id = db.Column(db.String)


# -------------------
# WORKER LOGIC
# -------------------

def run_worker():
    print("🟢 Worker started... Checking scheduled lessons every 30 seconds")

    while True:
        with app.app_context():
            try:
                # Find lessons that should be published
                lessons = Lesson.query.filter(
                    Lesson.status == "scheduled",
                    Lesson.publish_at <= func.now()
                ).all()

                if lessons:
                    print(f"⏰ Found {len(lessons)} scheduled lesson(s)")

                for lesson in lessons:
                    print(f"➡ Auto-publishing lesson: {lesson.id}")

                    # 🔓 AUTO-PUBLISH (NO ASSET VALIDATION)
                    lesson.status = "published"
                    lesson.published_at = datetime.utcnow()

                    # Find parent program
                    term = Term.query.get(lesson.term_id)
                    if term:
                        program = Program.query.get(term.program_id)

                        # Auto-publish program if not already published
                        if program and program.status != "published":
                            program.status = "published"
                            program.published_at = datetime.utcnow()
                            print(f"📢 Program auto-published: {program.id}")

                db.session.commit()

            except Exception as e:
                db.session.rollback()
                print("❌ Worker error:", e)

        time.sleep(30)


if __name__ == "__main__":
    run_worker()

from flask import Blueprint, request, jsonify, session, redirect, render_template, url_for, flash
from db import db
from models import Program, Term, Lesson, ProgramAsset, LessonAsset
from datetime import datetime
import uuid
from sqlalchemy.exc import IntegrityError

api_routes = Blueprint("api", __name__)

# -----------------------
# HELPER VALIDATIONS
# -----------------------

def program_has_required_posters(program):
    assets = ProgramAsset.query.filter_by(
        program_id=program.id,
        language=program.language_primary,
        asset_type="poster"
    ).all()

    variants = {a.variant for a in assets}
    return "portrait" in variants and "landscape" in variants


def lesson_has_required_thumbnails(lesson):
    assets = LessonAsset.query.filter_by(
        lesson_id=lesson.id,
        language=lesson.content_language_primary,
        asset_type="thumbnail"
    ).all()

    variants = {a.variant for a in assets}
    return "portrait" in variants and "landscape" in variants


# -----------------------
# CREATE ENTITIES (API)
# -----------------------

@api_routes.route("/programs", methods=["POST"])
def create_program():
    data = request.json
    program = Program(
        title=data["title"],
        description=data.get("description"),
        language_primary=data["language_primary"],
        languages_available=data["languages_available"],
        status="draft"
    )
    db.session.add(program)
    db.session.commit()
    return jsonify({"message": "Program created", "id": program.id})


@api_routes.route("/terms", methods=["POST"])
def create_term():
    data = request.json
    term = Term(
        program_id=data["program_id"],
        term_number=data["term_number"],
        title=data.get("title")
    )
    db.session.add(term)
    db.session.commit()
    return jsonify({"message": "Term created", "id": term.id})


@api_routes.route("/lessons", methods=["POST"])
def create_lesson():
    data = request.json
    lesson = Lesson(
        term_id=data["term_id"],
        lesson_number=data["lesson_number"],
        title=data["title"],
        content_type=data["content_type"],
        duration_ms=data.get("duration_ms"),
        is_paid=data.get("is_paid", False),
        content_language_primary=data["content_language_primary"],
        content_languages_available=data["content_languages_available"],
        content_urls_by_language=data["content_urls_by_language"],
        status="draft"
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify({"message": "Lesson created", "id": lesson.id})


# -----------------------
# PUBLISHING (API)
# -----------------------

@api_routes.route("/lessons/<lesson_id>/publish", methods=["POST"])
def publish_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"code": "NOT_FOUND", "message": "Lesson not found"}), 404

    if not lesson_has_required_thumbnails(lesson):
        return jsonify({
            "code": "ASSETS_MISSING",
            "message": "Lesson must have portrait and landscape thumbnails before publishing"
        }), 400

    lesson.status = "published"
    lesson.published_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Lesson published"})


@api_routes.route("/programs/<program_id>/publish", methods=["POST"])
def publish_program(program_id):
    program = Program.query.get(program_id)

    if not program:
        return jsonify({"code": "NOT_FOUND", "message": "Program not found"}), 404

    if not program_has_required_posters(program):
        return jsonify({
            "code": "ASSETS_MISSING",
            "message": "Program must have portrait and landscape posters before publishing"
        }), 400

    program.status = "published"
    if not program.published_at:
        program.published_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"message": "Program published"})


# -----------------------
# ASSET MANAGEMENT (API)
# -----------------------

@api_routes.route("/programs/<program_id>/assets", methods=["POST"])
def add_program_asset(program_id):
    data = request.json

    asset = ProgramAsset(
        id=str(uuid.uuid4()),
        program_id=program_id,
        language=data["language"],
        variant=data["variant"],
        asset_type="poster",
        url=data["url"]
    )

    db.session.add(asset)
    db.session.commit()

    return jsonify({"message": "Program asset added", "id": asset.id})


@api_routes.route("/lessons/<lesson_id>/assets", methods=["POST"])
def add_lesson_asset(lesson_id):
    data = request.json

    asset = LessonAsset(
        id=str(uuid.uuid4()),
        lesson_id=lesson_id,
        language=data["language"],
        variant=data["variant"],
        asset_type="thumbnail",
        url=data["url"]
    )

    db.session.add(asset)
    db.session.commit()

    return jsonify({"message": "Lesson asset added", "id": asset.id})


# -------------------------------
# PUBLIC CATALOG API (READ-ONLY)
# -------------------------------

@api_routes.route("/catalog/programs", methods=["GET"])
def list_catalog_programs():
    query = db.session.query(Program).join(Term).join(Lesson).filter(
        Lesson.status == "published"
    ).group_by(Program.id).order_by(Program.published_at.desc())

    programs = query.all()

    result = []
    for program in programs:
        term_count = Term.query.filter_by(program_id=program.id).count()
        lesson_count = db.session.query(Lesson).join(Term).filter(
            Term.program_id == program.id,
            Lesson.status == "published"
        ).count()

        result.append({
            "id": program.id,
            "title": program.title,
            "term_count": term_count,
            "lesson_count": lesson_count
        })

    return jsonify({"data": result})


# --------------------
# ADMIN UI
# --------------------

@api_routes.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", role=session.get("role"))


@api_routes.route("/ui/programs")
def ui_programs():
    if "user" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    programs = Program.query.all()
    return render_template("programs.html", programs=programs)


@api_routes.route("/ui/programs/<program_id>")
def ui_program_detail(program_id):
    if "user" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    program = Program.query.get_or_404(program_id)
    terms = Term.query.filter_by(program_id=program.id).order_by(Term.term_number).all()

    for term in terms:
        term.lessons = Lesson.query.filter_by(term_id=term.id).order_by(Lesson.lesson_number).all()

    return render_template("program_detail.html", program=program, terms=terms)


@api_routes.route("/ui/lessons/<lesson_id>")
def ui_lesson_detail(lesson_id):
    if "user" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template("lesson.html", lesson=lesson)


# -----------------------
# UI PUBLISHING
# -----------------------

@api_routes.route("/ui/lessons/<lesson_id>/publish", methods=["POST"])
def ui_publish_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if not lesson_has_required_thumbnails(lesson):
        flash("Lesson must have portrait and landscape thumbnails", "error")
        return redirect(url_for("api.ui_lesson_detail", lesson_id=lesson.id))

    lesson.status = "published"
    lesson.published_at = datetime.utcnow()
    db.session.commit()

    flash("Lesson published!", "success")
    return redirect(url_for("api.ui_lesson_detail", lesson_id=lesson.id))


@api_routes.route("/ui/programs/<program_id>/publish", methods=["POST"])
def ui_publish_program(program_id):
    program = Program.query.get_or_404(program_id)

    if not program_has_required_posters(program):
        flash("Program must have portrait and landscape posters", "error")
        return redirect(url_for("api.ui_program_detail", program_id=program.id))

    program.status = "published"
    if not program.published_at:
        program.published_at = datetime.utcnow()

    db.session.commit()
    flash("Program published!", "success")
    return redirect(url_for("api.ui_program_detail", program_id=program.id))


# -----------------------
# UI CREATION
# -----------------------

@api_routes.route("/ui/programs/create", methods=["GET", "POST"])
def ui_create_program():
    if request.method == "POST":
        program = Program(
            title=request.form["title"],
            description="Created from UI",
            language_primary=request.form["language"],
            languages_available=[request.form["language"]],
            status="draft"
        )
        db.session.add(program)
        db.session.commit()
        return redirect("/ui/programs")

    return render_template("create_program.html")


@api_routes.route("/ui/terms/create/<program_id>", methods=["GET", "POST"])
def ui_create_term(program_id):
    if request.method == "POST":
        term = Term(
            program_id=program_id,
            term_number=int(request.form["term_number"]),
            title=request.form.get("title")
        )

        try:
            db.session.add(term)
            db.session.commit()
            return redirect(f"/ui/programs/{program_id}")
        except IntegrityError:
            db.session.rollback()
            return render_template(
                "create_term.html",
                program_id=program_id,
                error="This term number already exists."
            )

    return render_template("create_term.html", program_id=program_id)


@api_routes.route("/ui/lessons/create/<term_id>", methods=["GET", "POST"])
def ui_create_lesson(term_id):
    if request.method == "POST":
        title = request.form["title"]
        lesson_number = int(request.form["lesson_number"])
        publish_at_raw = request.form.get("publish_at")

        if publish_at_raw:
            publish_at = datetime.fromisoformat(publish_at_raw)
            status = "scheduled"
        else:
            publish_at = None
            status = "draft"

        lesson = Lesson(
            term_id=term_id,
            lesson_number=lesson_number,
            title=title,
            content_type="video",
            duration_ms=300000,
            is_paid=False,
            content_language_primary="en",
            content_languages_available=["en"],
            content_urls_by_language={"en": "https://example.com/video"},
            status=status,
            publish_at=publish_at
        )

        try:
            db.session.add(lesson)
            db.session.commit()
            return redirect("/ui/programs")
        except IntegrityError:
            db.session.rollback()
            return render_template(
                "create_lesson.html",
                term_id=term_id,
                error="Lesson number already exists for this term."
            )

    return render_template("create_lesson.html", term_id=term_id)


# -----------------------
# UI ASSET UPLOAD
# -----------------------

@api_routes.route("/ui/programs/<program_id>/assets", methods=["POST"])
def ui_add_program_asset(program_id):
    asset = ProgramAsset(
        id=str(uuid.uuid4()),
        program_id=program_id,
        language=request.form["language"],
        variant=request.form["variant"],
        asset_type="poster",
        url=request.form["url"]
    )
    db.session.add(asset)
    db.session.commit()
    flash("Poster added!", "success")
    return redirect(url_for("api.ui_program_detail", program_id=program_id))


@api_routes.route("/ui/lessons/<lesson_id>/assets", methods=["POST"])
def ui_add_lesson_asset(lesson_id):
    asset = LessonAsset(
        id=str(uuid.uuid4()),
        lesson_id=lesson_id,
        language=request.form["language"],
        variant=request.form["variant"],
        asset_type="thumbnail",
        url=request.form["url"]
    )
    db.session.add(asset)
    db.session.commit()
    flash("Thumbnail added!", "success")
    return redirect(url_for("api.ui_lesson_detail", lesson_id=lesson_id))


# -----------------------
# PUBLIC CATALOG UI
# -----------------------

@api_routes.route("/catalog-ui")
def catalog_ui():
    programs = db.session.query(Program).join(Term).join(Lesson).filter(
        Lesson.status == "published"
    ).group_by(Program.id).all()

    data = []
    for program in programs:
        terms = Term.query.filter_by(program_id=program.id).order_by(Term.term_number).all()
        term_data = []

        for term in terms:
            lessons = Lesson.query.filter_by(
                term_id=term.id,
                status="published"
            ).order_by(Lesson.lesson_number).all()

            if lessons:
                term_data.append({
                    "term_number": term.term_number,
                    "term_title": term.title,
                    "lessons": lessons
                })

        data.append({
            "id": program.id,
            "title": program.title,
            "terms": term_data
        })

    return render_template("catalog.html", programs=data)

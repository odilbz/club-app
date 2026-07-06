from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import AcademyProgram, AcademyRegistration

academy_bp = Blueprint("academy", __name__, url_prefix="/academy")


@academy_bp.route("/")
def index():
    programs = AcademyProgram.query.all()
    return render_template("academy/index.html", programs=programs)


@academy_bp.route("/register/<int:program_id>", methods=["POST"])
@login_required
def register(program_id):
    program = AcademyProgram.query.get_or_404(program_id)

    existing = AcademyRegistration.query.filter_by(
        user_id=current_user.id, program_id=program.id
    ).first()
    if existing:
        flash("أنت مسجّل بالفعل في هذا البرنامج.", "info")
        return redirect(url_for("academy.index"))

    registration = AcademyRegistration(
        user_id=current_user.id, program_id=program.id,
        status="confirmed" if program.is_free else "pending",
    )
    db.session.add(registration)
    db.session.commit()

    if program.is_free:
        flash(f"تم تسجيلك بنجاح في \"{program.name}\" (برنامج مجاني).", "success")
        return redirect(url_for("academy.index"))

    return redirect(url_for("payment.checkout", order_type="registration", order_id=registration.id))

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            flash("الرجاء تعبئة جميع الحقول.", "danger")
            return redirect(url_for("auth.register"))
        if password != confirm:
            flash("كلمتا المرور غير متطابقتين.", "danger")
            return redirect(url_for("auth.register"))
        if len(password) < 6:
            flash("يجب أن تكون كلمة المرور 6 أحرف على الأقل.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("هذا البريد الإلكتروني مسجل مسبقًا.", "danger")
            return redirect(url_for("auth.register"))

        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("البريد الإلكتروني أو كلمة المرور غير صحيحة.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(f"مرحبًا بعودتك، {user.full_name}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.home"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for("auth.login"))

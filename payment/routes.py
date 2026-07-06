from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from extensions import db
from models import SavedCard, Order, AcademyRegistration

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")


def _get_target(order_type, order_id):
    """يرجع الكائن (طلب شراء أو تسجيل أكاديمية) والمبلغ والوصف."""
    if order_type == "order":
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id:
            abort(403)
        return order, order.total, "طلب من متجر النادي"

    if order_type == "registration":
        reg = AcademyRegistration.query.get_or_404(order_id)
        if reg.user_id != current_user.id:
            abort(403)
        return reg, reg.program.price, f"اشتراك أكاديمية — {reg.program.name}"

    abort(404)


@payment_bp.route("/checkout/<order_type>/<int:order_id>")
@login_required
def checkout(order_type, order_id):
    target, amount, description = _get_target(order_type, order_id)
    cards = SavedCard.query.filter_by(user_id=current_user.id).all()
    service_fee = 100 if amount else 0
    return render_template(
        "payment/checkout.html", cards=cards, amount=amount, description=description,
        service_fee=service_fee, total=amount + service_fee,
        order_type=order_type, order_id=order_id,
    )


@payment_bp.route("/add-card", methods=["POST"])
@login_required
def add_card():
    # ملاحظة أمان: هذا نموذج Mock تجريبي فقط، لا يُرسل أي رقم بطاقة حقيقي هنا.
    # في الإنتاج الحقيقي: استعمل بوابة دفع معتمدة، ولا تخزّن رقم البطاقة الكامل أبدًا.
    raw_number = request.form.get("card_number", "").replace(" ", "")
    expiry = request.form.get("expiry", "").strip()
    order_type = request.form.get("order_type")
    order_id = request.form.get("order_id")

    if len(raw_number) < 4 or not expiry:
        flash("بيانات البطاقة غير صحيحة.", "danger")
        return redirect(url_for("payment.checkout", order_type=order_type, order_id=order_id))

    card = SavedCard(user_id=current_user.id, brand="VISA",
                       last4=raw_number[-4:], expiry=expiry)
    db.session.add(card)
    db.session.commit()

    flash("تمت إضافة البطاقة بنجاح.", "success")
    return redirect(url_for("payment.checkout", order_type=order_type, order_id=order_id))


@payment_bp.route("/confirm/<order_type>/<int:order_id>", methods=["POST"])
@login_required
def confirm(order_type, order_id):
    target, amount, description = _get_target(order_type, order_id)
    card_id = request.form.get("card_id")

    if not card_id:
        flash("الرجاء اختيار بطاقة دفع.", "warning")
        return redirect(url_for("payment.checkout", order_type=order_type, order_id=order_id))

    # محاكاة عملية الدفع (Mock) — لا يوجد اتصال ببوابة دفع حقيقية هنا
    if order_type == "order":
        target.status = "paid"
    else:
        target.status = "paid"

    db.session.commit()
    flash("تم الدفع بنجاح! شكرًا لك.", "success")
    return redirect(url_for("payment.success", order_type=order_type, order_id=order_id))


@payment_bp.route("/success/<order_type>/<int:order_id>")
@login_required
def success(order_type, order_id):
    target, amount, description = _get_target(order_type, order_id)
    return render_template("payment/success.html", amount=amount, description=description)

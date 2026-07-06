from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user

from extensions import db
from models import Product, Order, OrderItem

store_bp = Blueprint("store", __name__, url_prefix="/store")


def _get_cart():
    return session.setdefault("cart", {})  # {product_id (str): quantity}


@store_bp.route("/")
def index():
    category = request.args.get("category")
    query = Product.query.filter_by(in_stock=True)
    if category and category != "الكل":
        query = query.filter_by(category=category)

    products = query.all()
    categories = ["الكل"] + sorted({p.category for p in Product.query.all()})
    return render_template("store/index.html", products=products, categories=categories,
                            active_category=category or "الكل")


@store_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = _get_cart()
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session.modified = True
    flash(f"تمت إضافة \"{product.name}\" إلى السلة.", "success")
    return redirect(request.referrer or url_for("store.index"))


@store_bp.route("/cart")
def cart():
    cart_data = _get_cart()
    items = []
    total = 0
    for pid, qty in cart_data.items():
        product = Product.query.get(int(pid))
        if not product:
            continue
        subtotal = product.price * qty
        total += subtotal
        items.append({"product": product, "quantity": qty, "subtotal": subtotal})
    return render_template("store/cart.html", items=items, total=total)


@store_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    return redirect(url_for("store.cart"))


@store_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart_data = _get_cart()
    if not cart_data:
        flash("السلة فارغة.", "warning")
        return redirect(url_for("store.index"))

    order = Order(user_id=current_user.id, status="pending")
    total = 0
    for pid, qty in cart_data.items():
        product = Product.query.get(int(pid))
        if not product:
            continue
        item = OrderItem(product_id=product.id, product_name=product.name,
                           quantity=qty, price=product.price)
        order.items.append(item)
        total += product.price * qty

    order.total = total
    db.session.add(order)
    db.session.commit()

    session["cart"] = {}
    session.modified = True

    return redirect(url_for("payment.checkout", order_type="order", order_id=order.id))

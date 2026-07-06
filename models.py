from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="user", lazy=True)
    registrations = db.relationship("AcademyRegistration", backref="user", lazy=True)
    cards = db.relationship("SavedCard", backref="user", cascade="all, delete-orphan", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    """منتج فمتجر النادي (قمصان، إكسسوارات...)."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="عام")
    price = db.Column(db.Float, nullable=False)
    emoji = db.Column(db.String(10), default="🛍️")  # أيقونة بسيطة بدل الصورة
    description = db.Column(db.String(300), default="")
    in_stock = db.Column(db.Boolean, default=True)


class AcademyProgram(db.Model):
    """برنامج تدريبي فالأكاديمية."""
    __tablename__ = "academy_programs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age_group = db.Column(db.String(30), nullable=False)  # مثال: "تحت 9 سنوات"
    coach = db.Column(db.String(100), nullable=False)
    sessions_per_week = db.Column(db.Integer, default=2)
    price = db.Column(db.Float, nullable=True)  # None = مجاني
    description = db.Column(db.String(300), default="")

    registrations = db.relationship(
        "AcademyRegistration", backref="program", cascade="all, delete-orphan", lazy=True
    )

    @property
    def is_free(self):
        return self.price is None or self.price == 0


class AcademyRegistration(db.Model):
    """تسجيل مستخدم فبرنامج أكاديمية."""
    __tablename__ = "academy_registrations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("academy_programs.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending / paid / confirmed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SavedCard(db.Model):
    """بطاقة دفع محفوظة (نسخة تجريبية Mock — لا تُخزَّن أي بيانات بطاقة حقيقية).

    ملاحظة أمان مهمة: هذا نموذج تجريبي فقط لأغراض العرض. في بيئة إنتاج حقيقية
    يجب استخدام بوابة دفع معتمدة (مثل CIB/Edahabia محليًا أو Stripe عالميًا)
    ولا يجب أبدًا تخزين رقم البطاقة الكامل أو CVV في قاعدة بياناتك الخاصة.
    """
    __tablename__ = "saved_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    brand = db.Column(db.String(20), default="VISA")
    last4 = db.Column(db.String(4), nullable=False)
    expiry = db.Column(db.String(7), nullable=False)  # MM/YYYY


class Order(db.Model):
    """طلب شراء من متجر النادي."""
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), default="pending")  # pending / paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan", lazy=True)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(150))  # لقطة من اسم المنتج وقت الشراء
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

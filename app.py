import os
from flask import Flask
from config import Config, DATA_DIR
from extensions import db, login_manager
from models import User, Product, AcademyProgram


def seed_data():
    """بيانات تجريبية أولية (تُضاف مرة واحدة فقط إذا كانت الجداول فارغة)."""
    if Product.query.count() == 0:
        db.session.add_all([
            Product(name="القميص الرسمي — نسخة اللاعبين", category="قمصان",
                     price=6500, emoji="👕", description="القميص الرسمي لموسم 2026."),
            Product(name="وشاح المشجعين الرسمي", category="إكسسوارات",
                     price=1200, emoji="🧣", description="وشاح صوفي بألوان النادي."),
            Product(name="طقم أطفال — مقاسات 4-12", category="أطفال",
                     price=3800, emoji="👶", description="طقم رسمي مخصص للأطفال."),
            Product(name="قبعة الشعار الرسمية", category="إكسسوارات",
                     price=900, emoji="🧢", description="قبعة قطنية بشعار النادي."),
        ])

    if AcademyProgram.query.count() == 0:
        db.session.add_all([
            AcademyProgram(name="برنامج الناشئين", age_group="تحت 9 سنوات",
                             coach="سفيان بلعيد", sessions_per_week=3, price=None,
                             description="تأسيس أساسيات كرة القدم للأطفال."),
            AcademyProgram(name="برنامج الشباب", age_group="تحت 15 سنة",
                             coach="كريم زيتوني", sessions_per_week=4, price=3000,
                             description="تدريب تكتيكي وبدني متقدم."),
            AcademyProgram(name="تخصص حراسة المرمى", age_group="كل الأعمار",
                             coach="ياسين مرابط", sessions_per_week=2, price=2500,
                             description="تدريب متخصص لحراس المرمى."),
        ])

    db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(os.path.join(DATA_DIR, "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from auth.routes import auth_bp
    from main.routes import main_bp
    from store.routes import store_bp
    from academy.routes import academy_bp
    from payment.routes import payment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(academy_bp)
    app.register_blueprint(payment_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

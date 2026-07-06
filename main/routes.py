from flask import Blueprint, render_template
from models import Product, AcademyProgram

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    featured_products = Product.query.limit(4).all()
    featured_programs = AcademyProgram.query.limit(2).all()
    return render_template(
        "main/home.html",
        featured_products=featured_products,
        featured_programs=featured_programs,
    )

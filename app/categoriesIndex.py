from flask import render_template
from app.models.category import Category

from .models.product import Product

from flask import Blueprint
bp = Blueprint('categoriesIndex', __name__)


@bp.route('/CatProducts/<catName>')
def CatProducts(catName):
    # get all available products for sale:
    productsCat = Product.get_by_category(catName)
    return render_template('sub_cat.html',
                           avail_products=productsCat)
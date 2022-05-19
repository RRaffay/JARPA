from flask import render_template, redirect, url_for, flash, request 
from flask_paginate import Pagination, get_page_parameter
from app.models.category import Category
from app.users import LoginForm
from flask_login import current_user
import datetime
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, InputRequired, Length
from flask_babel import _, lazy_gettext as _l

from .models.product import Product
from .models.purchase import Purchase
from .models.user import User
from .models.seller import Seller
from .models.cart import Cart
from .models.order import Order
from .models.reviews_product import Reviews_Product

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/', defaults ={"list_sort":0} ,methods=['GET', 'POST'])
@bp.route('/<list_sort>', methods=['GET', 'POST'])
def index(list_sort):

    searchQuery = request.args.get('sq')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # if search query 
    
    
    if searchQuery:
        # implement way to filter products
        products = Product.get_all()
        products = [product for product in products if searchQuery.lower() in product.name.lower()]
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
    elif list_sort == '1':
        products = Product.get_by_offset_sort((page-1)*30, 'price', 'ASC')
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
    elif list_sort == '2':
        products = Product.get_by_offset_sort((page-1)*30, 'price', 'DESC')
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
    elif list_sort == '3':
        products = Product.get_all()
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
        products = sorted(products, key=lambda x: x[0], reverse=True)
    elif list_sort == '4':
        products = Product.get_all()
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
        products = sorted(products, key=lambda x: x[0])
    elif list_sort == '5':
        products = Product.get_by_offset_sort((page-1)*30, 'name', 'ASC')
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
    elif list_sort == '6':
        products = Product.get_by_offset_sort((page-1)*30, 'name', 'DESC')
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
    else:
        products = Product.get_by_offset_sort((page-1)*30, 'name', 'ASC')
        products = [[Product.get_avg_rating(product.pid),product] for product in products]
   
   
    # get all available products for sale:
    #products = Product.get_all()
    # Get the search term
    searchQuery = request.args.get('sq')
    # if search query 
    if searchQuery:
        # implement way to filter products
        products = [product for product in products if searchQuery.lower() in product[1].name.lower()]

    
    
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(current_user.id, datetime.datetime(2020, 12, 31, 0, 0, 0))
    else:
        purchases = None

    
    # if price is set to true, sort by price
    #products = [[Product.get_avg_rating(product.pid),product] for product in products]

    ##################  Products pagination ##################
    total_products = Product.get_number_of_products()
    pagination = Pagination(page=page, total=total_products, record_name='products',per_page=30)
    #################################################################


# render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases,
                           l = len(products),
                           pagination=pagination)


@bp.route('/ProductPages/<productID>')
def ProductPages(productID):
    
    user_creator = False
    product = Product.get(productID)
    user = User.get(product.creator_id)
    sellers = Seller.get_seller_by_pid(productID)
    sellerNames = []
    if current_user.is_authenticated:
        user_seller = User.is_seller(current_user.id)
    else:
        user_seller = False

    if current_user.is_authenticated:
        if user.id == current_user.id:
            user_creator = True

    
    for idx in range(len(sellers)):
        seller = sellers[idx]
        sellerNames.append([0,0])
        sellerNames[idx][0] = User.get(seller.seller_id)
        sellerNames[idx][1] = seller.quantity
        print(sellerNames[idx])

    reviews = Product.ratings(product.pid)

    num_ratings = len(reviews)
    average_rating = sum(int(review[0]) for review in reviews) / (num_ratings if num_ratings else 1)

    return render_template('productpage.html',
                            product=product,
                            user=user,
                            sellerNames=sellerNames,
                            reviews=reviews,
                            num_ratings=num_ratings,
                            average_rating=average_rating,
                            user_seller=user_seller,
                            user_creator=user_creator)


class ProductForm(FlaskForm):
    productName = StringField(_l('Product Name'), validators=[DataRequired()])
    description = StringField(_l('Product Description'), validators=[DataRequired()])
    image = StringField(_l('Product Image'), validators=[DataRequired()])
    price = FloatField(_l('Product Price'), validators=[InputRequired()])
    category = StringField(_l('Product Category'), validators=[DataRequired()])
    submit = SubmitField(_l('Add Product'))

@bp.route('/createProduct', methods=['GET', 'POST'])
def createProduct():
    form = ProductForm()
    if form.validate_on_submit(): 
            if Product.addProduct(
                form.productName.data,
                form.description.data,
                form.image.data,
                form.price.data,
                form.category.data,
                current_user.id
            ):
                flash('Product added successfully!')       
                return redirect(url_for('index.index'))

    return render_template('createProduct.html', form=form)

class UpdateProductForm(FlaskForm):
    productName = StringField(_l('Product Name'), validators=[DataRequired()])
    description = StringField(_l('Product Description'), validators=[DataRequired()])
    image = StringField(_l('Product Image'), validators=[DataRequired()])
    price = FloatField(_l('Product Price'), validators=[InputRequired()])
    category = StringField(_l('Product Category'), validators=[DataRequired(), Length(max=50)])
    submit = SubmitField(_l('Update Product'))

@bp.route('/updateProduct/<pid>', methods=['GET', 'POST'])
def updateProduct(pid):
    print("function is working")
    product = Product.get(pid)
    form = UpdateProductForm()

    if request.method == 'GET':
        form.productName.data = product.name
        form.description.data = product.description
        form.image.data = product.image
        form.price.data = product.price
        form.category.data = product.category


    
    if form.validate_on_submit(): 
            if Product.updateProduct(
                form.productName.data,
                form.description.data,
                form.image.data,
                form.price.data,
                form.category.data,
                current_user.id
            ):
                flash('Product updated successfully!')  
                # Return to product page     
            return redirect(url_for('index.ProductPages', productID=pid))

    return render_template('updateProduct.html', form=form)

class ReviewProductForm(FlaskForm):
    rating = FloatField(_l('Rating (Out of 5)'), validators=[InputRequired(), NumberRange(min=1, max=5)])
    reviewdescription = StringField(_l('Description'), validators=[DataRequired()])
    submit = SubmitField(_l('Add Review'))

@bp.route('/addProductReview/<pid>', methods=['GET', 'POST'])
def addProductReview(pid):
    # if current_user.is_authenticated:
    form = ReviewProductForm()
    product = Product.get(pid)
    if form.validate_on_submit():
        result = Reviews_Product.addProductReviewSQL(
            form.rating.data,
            form.reviewdescription.data,
            current_user.id,
            product.pid,
        )

        if result:
            return redirect(url_for('index.ProductPages', productID=pid))
        else:
            flash('You can only review each product once!')

    return render_template('AddProductReview.html', form = form)

@bp.route('/removeProductReview/<pid>', methods=['GET', 'POST'])
def removeProductReview(pid):
    Reviews_Product.removeProductReview(current_user.id, pid)
    return redirect(url_for('users.profile'))

@bp.route('/updateProductReview/<pid>', methods=['GET', 'POST'])
def updateProductReview(pid):
    form = ReviewProductForm()
    if form.validate_on_submit():
        result = Reviews_Product.updateProductReview(form.rating.data, form.reviewdescription.data, current_user.id, pid)

        if result:
            return redirect(url_for('users.profile', productID=pid))
        else:
            flash('Error updating review!')

    return render_template('updateProductReview.html', form = form)

@bp.route('/addSellerReview/<sid>', methods=['GET', 'POST'])
def addSellerReview(sid):
    # if current_user.is_authenticated:
    form = ReviewProductForm()
    if form.validate_on_submit():
        result = Reviews_Product.addSellerReview(
            form.rating.data,
            form.reviewdescription.data,
            current_user.id,
            sid,
        )

        if result:
            return redirect(url_for('users.publicProfile', id= sid))
        else:
            flash('You can only review each seller once!')

    return render_template('addSellerReview.html', form = form)

@bp.route('/removeSellerReview/<sid>', methods=['GET', 'POST'])
def removeSellerReview(sid):
    Reviews_Product.removeSellerReview(current_user.id, sid)
    return redirect(url_for('users.profile'))

@bp.route('/updateSellerReview/<sid>', methods=['GET', 'POST'])
def updateSellerReview(sid):
    form = ReviewProductForm()
    if form.validate_on_submit():
        result = Reviews_Product.updateSellerReview(form.rating.data, form.reviewdescription.data, current_user.id, sid)

        if result:
            return redirect(url_for('users.profile', id=current_user.id))
        else:
            flash('Error updating review!')

    return render_template('updateProductReview.html', form = form)

@bp.route('/categoriesPage')
def categoriesPage():
    # get all available products for sale:
    categories = Category.get_all()
    catSearchQuery = request.args.get('cq')

    if catSearchQuery:
        # implement way to filter categories
        categories = [cat for cat in categories if catSearchQuery in cat.name]


    ################## Trying categories pagination ##################
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=len(categories), record_name='categories',per_page=15)
    categories = categories[page*15-15:page*15]
    #################################################################

    # find the products current user has bought:
    return render_template('categories.html',
                           categoriesIn=categories,
                           pagination=pagination)

@bp.route('/CatProducts/<catName>')
def CatProducts(catName):
    # get all available products for sale by category:
    productsCat = Product.get_by_category(catName)
    return render_template('sub_cat.html',
                           avail_products=productsCat,
                           catName = catName)


#Cart


#passing in display elements for cart page and calculating total price
@bp.route('/Cart/<uid>')
def cart(uid): 
    productList = [] 
    productsCart = Cart.displayCart(uid)
    totalPrice = [p.price * p.quantity for p in productsCart]
    for i in range(len(productsCart)):
        productList.append([productsCart[i], totalPrice[i]])
    return render_template('carts.html', allProds = productList, total = sum(totalPrice))

#add to cart function for product page
@bp.route('/addtoCart/<uid>/<quantity>/<pid>')
def AddToCart(uid, quantity, pid):
    #quantity = request.form['quant']
    Cart.checkQuantity(uid, quantity, pid)
    return redirect(url_for('index.cart', uid = uid))

#backend database quantity updating for HasInCart
@bp.route('/updateQuantity', methods=['POST'])
def updateQuantity():
    quant = request.form['quant']
    pid = request.form['product_id']
    id = current_user.id
    Cart.updateQuantity(id, quant, pid)
    return redirect(url_for('index.cart', uid = id))

@bp.route('/applyCoupon', methods=['POST'])
def applyCoupon():
    coupon = request.form['coupon']
    Cart.applyCoupon(current_user.id, coupon)
    print("Coupon applied", coupon)
    return redirect(url_for('index.cart', uid = current_user.id))

#delete item from cart
@bp.route('/deleteCart', methods = ['POST'])
def deleteCart():
    id = current_user.id 
    pid = request.form['delproduct_id']
    Cart.deleteCart(id, pid)
    return redirect(url_for('index.cart', uid = id))


#Order
@bp.route('/order/<uid>')
def SubmitOrder(uid):
    Order.sellerInv(uid)
    orderPage = Order.displayOrder(uid)
    if not orderPage:
        orderPage = [[]]

    print(orderPage)
    return render_template('orders.html', allOrders = orderPage, User = User, Product = Product, Order = Order)
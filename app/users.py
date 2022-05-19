from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from app.models.purchase import Purchase
from app.models.reviews_product import Reviews_Product
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.user import User
from .models.product import Product
from .models.order import Order
from .models.reviews_product import Reviews_Product

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        print("USER:", user)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    adrs = StringField(_l('Address'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('Already a user with this email.'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.adrs.data):
                
            user = User.get_by_auth(form.email.data, form.password.data)
            login_user(user)
            return redirect(url_for('index.index'))
            
            # return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

class UpdateForm(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password (not shown to protect your privacy... leave both password fields blank if you do not want to change your password)'), validators=[])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[
                                           EqualTo('password')])
    adrs = StringField(_l('Address'), validators=[DataRequired()])
    submit = SubmitField(_l('Update'))

    def validate_email(self, email):
        if User.email_exists_not_uid(email.data, current_user.id):
            raise ValidationError(_('Already a user with this email.'))


@bp.route('/update', methods=['GET', 'POST'])
def update():
    # user isn't logged in
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    user = User.get(current_user.id)
    form = UpdateForm()

    if request.method == 'GET':
        form.email.data = user.email
        form.firstname.data = user.firstname
        form.lastname.data = user.lastname
        form.adrs.data = user.adrs

    if form.validate_on_submit():
        passChanged = form.password.data is not None and len(form.password.data) > 0
        print("PASSWORD CHANGE:", passChanged, form.password.data, "END")

        result = User.update(user.id, form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.adrs.data,
                         passChanged)

        if result:
            flash('Updated profile')
            return redirect(url_for('users.profile'))
    
    return render_template('update.html', title='Update', form=form)

@bp.route('/profile')
def profile():
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(current_user.id, "12/31/20 23:59")
        sells = Product.sells(current_user.id)
        reviews = User.ratings(current_user.id)
        seller = User.is_seller(current_user.id)
        creator = User.is_creator(current_user.id)
        reviews_product = Reviews_Product.get_reviews_product(current_user.id)
        reviews_seller = Reviews_Product.get_reviews_seller(current_user.id)
    else:
        purchases = None
        sells = None
        reviews = None
        seller = None
        creator = None
        reviews_product = None
        reviews_seller = None

    users = User.all_users()

    return render_template('profile.html', purchase_history=purchases, users=users, seller=seller, sells=sells, reviews=reviews, reviews_product=reviews_product, reviews_seller=reviews_seller, Product=Product, User=User, creator=creator)

@bp.route('/updateBalance', methods=['POST'])
def updateBalance():
    amount = request.form['amt']
    current_user.balance += int(amount)
    User.updateBalance(current_user.id, current_user.balance)
    return redirect(url_for('users.profile'))

@bp.route('/clearBalance')
def clearBalance():
    current_user.balance = 0
    User.updateBalance(current_user.id, current_user.balance)
    return redirect(url_for('users.profile'))

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/publicProfile/<id>')
def publicProfile(id):
    user = User.get(id)
    seller = User.is_seller(user.id)
    sells = Product.sells(user.id)
    reviews = User.ratings(user.id)
    purchases = Purchase.get_all_by_uid_since(user.id, '2000-12-31')
    num_ratings = len(reviews)
    average_rating = sum(int(review[0]) for review in reviews) / (num_ratings if num_ratings else 1)
    return render_template('publicProfile.html', user=user, seller=seller, sells=sells, reviews=reviews, purchase_history=purchases, average_rating=average_rating, num_ratings=num_ratings, Product=Product, User=User)

@bp.route('/inventory')
def inventory():
    user = User.get(current_user.id)
    seller = User.is_seller(user.id)
    # All products sold definitely come from authenticated seller_id
    sells = Product.sells(user.id)
    # All orders definitely come from authenticated seller_id
    orders = Order.seller_orders(user.id)
    # pids in orders do not necessarily reference products in a seller's inventory
    has_orders = len(orders) >= 1

    searchprods = request.args.get('sqp')
    if searchprods:
        sells = [product for product in sells if searchprods.lower() in product[0].name.lower()]
    
    searchords = request.args.get('sqo')
    if searchords:
        orders = [order for order in orders if searchords.lower() in order[2][0].lower()]
    return render_template('inventory.html', user = user, seller = seller, sells = sells, orders = orders, has_orders = has_orders)


@bp.route('/editInventory')
def editInventory():
    user = User.get(current_user.id)
    seller = User.is_seller(user.id)
    sells = Product.sells(user.id)
    return render_template('editInventory.html', user=user, seller=seller, sells=sells)


@bp.route('/creations')
def creations():
    user = User.get(current_user.id)
    creator = User.is_creator(current_user.id)
    prods = Product.creator_products(current_user.id)

    searchQuery = request.args.get('sq')
    if searchQuery:
        prods = [product for product in prods if searchQuery in product.name]
    return render_template('creations.html', user=user, creator=creator, prods=prods)

@bp.route('/updateInventory/<pid>', methods=['POST'])
def updateInventory(pid):
    amount = request.form['amt']
    Product.seller_update(current_user.id, pid, amount)
    return redirect(url_for('users.editInventory'))

@bp.route('/deleteItem/<pid>')
def deleteItem(pid):
    Product.seller_remove(current_user.id, pid)
    return redirect(url_for('users.editInventory'))

@bp.route('/addItem/<pid>', methods=['POST'])
def addItem(pid):
    valid = Product.available_to_add_seller(current_user.id, pid)
    print(f'\n\nValid: {valid[0], valid[1]}\n\n')
    if valid[0]:
        amount = request.form['amt']
        Product.seller_add(current_user.id, pid, amount)
        return redirect(url_for('users.inventory'))
    else:
        return redirect(url_for('index.ProductPages', productID = pid))

    # num_ratings = len(reviews)
    # average_rating = sum(int(review[0]) for review in reviews) / (num_ratings if num_ratings else 1)

    # return render_template('publicProfile.html', user=user, seller=seller, sells=sells, reviews=reviews, purchase_history=purchases, num_ratings=num_ratings, average_rating=average_rating, Product=Product)

@bp.route('/changeFulfillment/<oid>/<pid>')
def changeFulfillment(oid, pid):
    order = Order.get(oid, pid)
    if order.fulfilled == True:
        Order.unfulfill(oid, pid)
    elif order.fulfilled == False:
        Order.fulfill(oid, pid)

    print(f'\n\n{type(order.fulfilled)}\n\n')
    return redirect(url_for('users.inventory'))

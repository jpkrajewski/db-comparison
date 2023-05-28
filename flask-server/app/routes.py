from app.models import User, Product, Review, Order, search_products, db
from app.analytics_utils import create_search_data_document

from flask import Blueprint, render_template, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient

client = MongoClient('mongo:27017')
mongo_db = client['analytics']  
collection_analytics_v1 = mongo_db['analytics_v1']  

views = Blueprint('views', __name__,
                  template_folder='templates')

analytics_apiv1 = Blueprint('analytics_apiv1', __name__, 
                          url_prefix='/apiv1')

@views.route('/products')
def products():
    keywords = request.args.get('keywords')
    if keywords is not None:
        keywords = keywords.replace(' ', '').split(',')
        products = search_products(keywords)
        document = create_search_data_document(keywords)
        collection_analytics_v1.insert_one(document)
    else:
        products = Product.query.all()
    return render_template('products.html', products=products)


@views.route('/products/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)


@views.route('/products/create', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        product = Product(
            name=name,
            price=float(price), 
            description=description)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('views.product_detail', id=product.id))
    return render_template('product_create.html')


@views.route('/products/<int:id>/edit', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        # Retrieve form data
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        
        # Update the product in the database
        db.session.commit()
        
        # Redirect to the product detail page
        return redirect(url_for('views.product_detail', id=product.id))
    
    return render_template('product_edit.html', product=product)


@views.route('/products/<int:id>/delete', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # Delete the product from the database
    db.session.delete(product)
    db.session.commit()
    
    # Redirect to the products list page
    return redirect(url_for('views.products'))

# Read all users
@views.route('/users', methods=['GET'])
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

# Read user details
@views.route('/users/<int:id>', methods=['GET'])
def user_details(id):
    user = User.query.get(id)
    return render_template('user_details.html', user=user)

# Delete a user
@views.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    try:
        Order.query.filter_by(user_id=user.id).delete()
        Review.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
    finally:
        return redirect(url_for('views.users'))

@views.route('/analytics', methods=['GET', 'POST'])
def analytics_page():
    documents = None
    if request.method == 'POST':
        field_name = request.form.get('field')
        operator = request.form.get('operator')
        search_value = request.form.get('value')

        if operator == '$in':
            search_value = search_value.split(',')

        documents = collection_analytics_v1.find({field_name: {operator: search_value}})
    return render_template('analytics.html', documents=documents)

@analytics_apiv1.route('/analytics', methods=['POST'])
def analytics():
    data = request.get_json()
    result = collection_analytics_v1.insert_one(data)
    if result.acknowledged:
        return jsonify(status='success', inserted_id=str(result.inserted_id))
    else:
        return jsonify(status='error')

import os
import logging
from faker import Faker

from flask import Flask

from app.models import db, User, Product, Order, OrderItem, Review
from app.routes import simple_page

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.register_blueprint(simple_page)
    configure_logging()
    configure_database(app)

    return app

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def configure_database(app):

    password_path = os.getenv('DATABASE_PASSWORD')
    with open(password_path, 'r') as file:
        password = file.read()

    if password is None:
        logging.error('DATABASE_PASSWORD environment variable is not set.')
        return

    database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if database_uri is None:
        logging.error('SQLALCHEMY_DATABASE_URI environment variable is not set.')
        return

    database_uri = database_uri.replace(
        'PASSWORD_PLACEHOLDER', 
        password
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    inspect_database(app)

def inspect_database(app):
    with app.app_context():
        # Create a SQLAlchemy metadata object
        has_records = User.query.first() is not None

        if has_records:
            # Perform actions if the table has records
            # ...
            pass
        else:
            logging.info('Seeding database.')
            seed_data()

def seed_data():
    fake = Faker()

    # Create users
    users = []
    for _ in range(100):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password()
        )
        users.append(user)
        db.session.add(user)

    # Create products
    products = []
    for _ in range(200):
        product = Product(
            name=fake.word(),
            price=fake.random_number(digits=2),
            description=fake.text()
        )
        products.append(product)
        db.session.add(product)

    # Create orders and order items
    for _ in range(100):
        user = fake.random_element(users)
        order = Order(
            user=user,
            order_date=fake.date_this_year(),
            total_amount=fake.random_number(digits=2)
        )
        db.session.add(order)

        for _ in range(2):
            product = fake.random_element(products)
            order_item = OrderItem(
                order=order,
                product=product,
                quantity=fake.random_int(min=1, max=5),
                price=product.price
            )
            db.session.add(order_item)

    # Create reviews
    for _ in range(100):
        user = fake.random_element(users)
        product = fake.random_element(products)
        review = Review(
            product=product,
            user=user,
            rating=fake.random_int(min=1, max=5),
            comment=fake.text()
        )
        db.session.add(review)

    # Commit the changes to the database
    db.session.commit()

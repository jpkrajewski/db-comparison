import os
import logging
import random
from datetime import datetime

from faker import Faker
from flask import Flask

from app.models import db, User, Product, Order, OrderItem, Review
from app.routes import views, analytics_apiv1
from pymongo import MongoClient

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.register_blueprint(views)
    app.register_blueprint(analytics_apiv1)
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

    with open(os.getenv('DATABASE_PASSWORD'), 'r') as file:
        password = file.read()

    if password is None:
        logging.error('DATABASE_PASSWORD environment variable is not set.')
        return

    database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if database_uri is None:
        logging.error(
            'SQLALCHEMY_DATABASE_URI environment variable is not set.'
        )
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

    client = MongoClient('mongo:27017')
    mongo_db = client['analytics']  
    collection_analytics_v1 = mongo_db['analytics_v1']

    documents = []

    for _ in range(500):
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)
        keywords = generate_keywords(random.choice([True, False]))
        document = {
            'action': 'search',
            'keywords_count': len(keywords),
            'keywords_items': keywords,
            'searched_at': fake.date_between(start_date=start_date, end_date=end_date)
        }
        documents.append(document)
    collection_analytics_v1.insert_many(documents)

def generate_keywords(is_list):
    fake = Faker()
    if is_list:
        num_keywords = random.randint(1, 5)  # Generate 1 to 5 keywords
        keywords = [fake.word() for _ in range(num_keywords)]
    else:
        keywords = fake.word()
    return keywords
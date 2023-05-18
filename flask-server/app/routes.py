from app.models import User, Review
from flask import render_template, request

import logging

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

simple_page = Blueprint('simple_page', __name__,
                        template_folder='templates')

@simple_page.route('/', defaults={'page': 'index'})
@simple_page.route('/<page>')
def show(page):
    try:
        users = User.query.all()

        # Retrieve all reviews
        reviews = Review.query.all()
        
        logging.info(users)
        logging.info(reviews)

        return {1: reviews, 2:users}
    except TemplateNotFound:
        abort(404)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/action_insert', methods=['GET', 'POST'])
# def action_insert():

#     return render_template('action_insert.html')


# @app.route('/action_search', methods=['GET', 'POST'])
# def action_search():
#      # Retrieve all users
#     users = User.query.all()

#     # Retrieve all reviews
#     reviews = Review.query.all()

#     return {1: reviews, 2:users}


# def todo():
#     try:
#         client.admin.command('ismaster')
#     except:
#         return "Server not available"
#     return "Hello from the MongoDB client!\n"



# @app.route('/blog')
# def listBlog():
#     global conn
#     if not conn:
#         conn = DBManager(password_file='/run/secrets/db-password')
#         conn.populate_db()
#     rec = conn.query_titles()

#     response = ''
#     for c in rec:
#         response = response  + '<div>   Hello  ' + c + '</div>'

#     response += '\n\n\n\n'

#     db = client["contact_form"]
#     collection = db["messages"]

#     messages = collection.find()

#     for message in messages:
#         logging.debug(message)
#         response += '<div>   Hello  ' + str(message) + '</div>' 
    
#     return response
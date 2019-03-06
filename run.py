# run.py

from flask import Flask, flash, request,Response
from flask_sqlalchemy import SQLAlchemy


import os
import json


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'LibraryDataBase.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


class Book(db.Model):
    """
    This is a class for Book
    """

    __table_name = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    author = db.Column(db.String(64), index=True)
    category = db.Column(db.String(64), index=True)
    pages = db.Column(db.Integer, index=True)
    serial_no = db.Column(db.Integer, index=True)
    publisher = db.Column(db.String(64), index=True)


class User(db.Model):
    """
    This is a user class.
    """

    __tablename__ = 'members'
    id = db.Column(db.Integer, index=True, primary_key=True)
    user_name = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64),index=True, unique=True)
    address = db.Column(db.String(64), index=True)


class Acquire(db.Model):
    """
    This is for acquire table class
    """
    __tablename__ = 'acquires'
    id = db.Column(db.Integer, index=True, primary_key=True)
    user_name = db.Column(db.String(60), index = True)
    book_title = db.Column(db.String(60), index = True)
    serial_no = db.Column(db.Integer, index=True)


def to_json(data):
    obj={}
    obj["title"] = str(data.title)
    obj["author"] = str(data.author)
    obj["category"] = str(data.category)
    obj["pages"] = str(data.pages)
    obj["serial_no"] = str(data.title)
    obj["publisher"] = str(data.publisher)
    json_obj=json.dumps(obj)
    return Response(json_obj, mimetype="application/json")


def user_to_json(data):
    obj={}
    obj["user_name"] = str(data.user_name)
    obj["first_name"] = str(data.first_name)
    obj["last_name"] = str(data.last_name)
    obj["email"] = str(data.email)
    obj["address"] = str(data.address)
    json_obj=json.dumps(obj)
    return Response(json_obj, mimetype="application/json")


@app.route('/')
def index():
    return "<h1> Welcome to home <h1>"


@app.route('/acquire', methods=['POST'])
def Acquired():
    data = request.get_json()
    print(data)
    if all(key in data for key in ['user_name', 'serial_no']):
        book = Book.query.filter_by(serial_no=data["serial_no"]).first()
        members = User.query.filter_by(user_name=data["user_name"]).first()
        if book and members:
            acquires=Acquire(user_name=members.user_name, book_title=book.title,serial_no=book.serial_no)
            db.session.add(acquires)
            db.session.commit()
            return '<h1>  Book Acquired Successfully. :) <h1>'

    return 'Ooops! Something Went Wrong. :('

@app.route('/user/add', methods=['POST'])
def UserAdd():

    data = request.get_json()

    if all(key in data for key in ['user_name', 'first_name', 'last_name', 'email', 'address']):
        db.create_all()
        members = User(user_name=data['user_name'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        email=data['email'],
                        address=data['address'])


        db.session.add(members)
        db.session.commit()
        return '<h1> Member has been added succesfully! <h1>'
    return '<h1> Ooooops: Make Sure all Fields are filled! <h1>'


@app.route('/user/search', methods=['GET', 'POST'])
def UserSearch():

    key_value=request.args.get('user_name')
    if key_value:
        members=User.query.filter_by(user_name=key_value).first()

    key_value = request.args.get('email')
    if key_value:
        members = User.query.filter_by(title=key_value).first()
    if members:
        return user_to_json(members)

    return 'Sorry! Your Entered user is not out List!'


@app.route('/user/update', methods=['PUT'])
def UserUpdate():
    key_value = request.args.get('user_name')
    update_user_name = request.args.get('update')

    if key_value:
        members = User.query.filter_by(user_name=key_value).first()
        if members:
            members.user_name=update_user_name

    key_value = request.args.get('email')
    update_email = request.args.get('update')
    if key_value:
        members = User.query.filter_by(email=key_value).first()
        if members:
            members.user_name = update_email

    if members:
        db.session.add(members)
        db.session.commit()
        return user_to_json(members)

    return 'Sorry! Your Entered User is not in our List!'


@app.route('/user/delete', methods=['DELETE'])
def UserDelete():
    key_value = request.args.get('user_name')
    if key_value:
        members = User.query.filter_by(user_name=key_value).first()

    key_value = request.args.get('email')
    if key_value:
        members = User.query.filter_by(email=key_value).first()

    if members:
        db.session.delete(members)
        db.session.commit()
        return 'Member Removed Successfully!'

    return 'Ooops! not available in List!'

@app.route('/book/add', methods=['GET', 'POST'])
def BookAdd():

    data = request.get_json()
    if all(key in data for key in ['title', 'author', 'category', 'pages', 'serial_no', 'publisher']):
        book = Book(title=data['title'],
                        author=data['author'],
                        category=data['category'],
                        pages=data['pages'],
                        serial_no=data['serial_no'],
                        publisher=data['publisher'])

        db.session.add(book)
        db.session.commit()
        return '<h1> Book has been succesfully added! <h1>'
    return '<h1> Ooooops: Make Sure all Fields are filled! <h1>'


@app.route('/book/search', methods=['GET', 'POST'])
def BookSearch():

    key_value=request.args.get('author')
    if key_value:
        book=Book.query.filter_by(author=key_value).first()

    key_value = request.args.get('title')
    if key_value:
        book = Book.query.filter_by(title=key_value).first()

    key_value = request.args.get('category')
    if key_value:
        book = Book.query.filter_by(category=key_value).first()
    if book:
        return to_json(book)

    return 'Sorry! Your Entered Book is not available!'


@app.route('/book/update', methods=['GET', 'POST'])
def BookUpdate():
    key_value = request.args.get('author')
    update_author = request.args.get('update')

    if key_value:
        book = Book.query.filter_by(author=key_value).first()
        if book:
            book.author=update_author

    key_value = request.args.get('title')
    update_title = request.args.get('update')

    if key_value:
        book = Book.query.filter_by(title=key_value).first()
        if book:
            book.title=update_title

    key_value = request.args.get('category')
    update_category = request.args.get('update')
    if key_value:
        book = Book.query.filter_by(category=key_value).first()
        if book:
            book.category=update_category

    if book:
        db.session.add(book)
        db.session.commit()
        return to_json(book)

    return 'Sorry! Your Entered Book is not available!'


@app.route('/book/delete', methods=['DELETE'])
def BookDelete():
    key_value = request.args.get('author')

    if key_value:
        book = Book.query.filter_by(author=key_value).first()

    key_value = request.args.get('title')
    if key_value:
        book = Book.query.filter_by(title=key_value).first()

    key_value = request.args.get('category')
    if key_value:
        book = Book.query.filter_by(category=key_value).first()

    if book:
        db.session.delete(book)
        db.session.commit()
        return 'Book Deleted Successfully!'

    return 'Ooops! Your Book is not available.'


if __name__ == '__main__':
    db.create_all()
    app.run()

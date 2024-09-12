from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate


app = Flask(__name__)
# Step-1
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
db = SQLAlchemy()
db.init_app(app)
app.secret_key = '123'
migrate = Migrate(app, db)



# Step-2: Define User Schema
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=False,nullable=False)
    books = db.relationship('Book', backref='owner', lazy="select") # backref='owner': could be any attribute not just 'owner'
    # bacref: how to get data from of books of this user or vise verse: (will be understood in below code)
    # lazy: how tables will be get at database background (default is select) check it's types (https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html)
    
    def __init__(self, username):
        self.username = username

# Define Book Schema
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, title, user_id=None):
        self.title = title
        self.user_id = user_id


@app.route("/")
def run_all():
    ## Step-3
    # Create a new user
    new_user = User(username='mohamed Ayman')
    db.session.add(new_user)
    db.session.commit()
    print("Added User")

    # Add a book
    new_book = Book(title='Flask Book',user_id='1') # could specfiy also user_id=5 or owner=new_user
    # new_book = Book(title='Flask Book', user_id=new_user.id) 
    db.session.add(new_book)
    db.session.commit()
    print("Added Book")


    # [Add a book for user]
    user = User.query.get(new_user.id)
    book = Book.query.get(new_book.id)
    if user and book:
        book.user_id = user.id # add fk then submit
        db.session.commit()

    # what is backref? (to get books of a user without multible queries and vise-verse)
    user = User.query.filter_by(username='Ahmed Ayman2').first() # when getting user I can get his books also vise-verse(Book.owser.username)
    books = user.books # don't worry it's not error, it gets books of user

    for book in books:
        print(book.title)
        print(book.owner.username) # and username of a book
    
    return "Congratulations!!"

with app.app_context():
    db.create_all()
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
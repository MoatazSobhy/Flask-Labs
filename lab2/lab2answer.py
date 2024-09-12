from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
db = SQLAlchemy()
app.secret_key = '123'
db.init_app(app)


# Define User Schema
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    books = db.relationship('Book', backref='owner', lazy="select")

    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

# Define Book Schema
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.LargeBinary)  # Store images as BLOBs
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, title, image=None, user_id=None):
        self.title = title
        self.image = image
        self.user_id = user_id


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists!"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('view_books'))
        return "Invalid credentials!"
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    if 'user_id' in session.keys():
        session.pop('user_id')
        session.pop('is_admin')
    return redirect(url_for('login'))


# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' in session.keys():
        if request.method == 'POST':
            title = request.form['title']
            image = request.files['image'].read()  # Store image as BLOB
            new_book = Book(title=title, image=image, user_id=session['user_id'])
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('view_books'))
        return render_template('add_book.html')
    return redirect(url_for('login'))


# View Books
@app.route('/view_books')
def view_books():
    if 'user_id' in session.keys():
        user = User.query.get(session['user_id'])
        books = user.books
        return render_template('view_books.html', books=books)
    return redirect(url_for('login'))



# Delete Book
@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('view_books'))

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return "Access Denied!"
    users = User.query.all()
    books = Book.query.all()
    return render_template('admin_dashboard.html', users=users, books=books)

# Delete User
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('is_admin'):
        return "Access Denied!"
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Main Route (For testing and setup)
@app.route("/")
def run_all():
    # Create a new user (for testing purposes)
    new_user = User(username='Mohamed-Ayman', password='password')
    db.session.add(new_user)
    db.session.commit()
    print("Added User")

    # Add a book (for testing purposes)
    new_book = Book(title='Flask Book')
    db.session.add(new_book)
    db.session.commit()
    print("Added Book")

    # Associate book with user
    user = User.query.get(new_user.id)
    book = Book.query.get(new_book.id)
    if user and book:
        book.user_id = user.id
        db.session.commit()

    # Fetch books of user
    user = User.query.filter_by(username='Ahmed Ayman').first()
    books = user.books

    for book in books:
        print(book.title)
        print(book.owner.username)

    return "Congratulations!!"

# Initialize Database
with app.app_context():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)

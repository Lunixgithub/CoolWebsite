from flask import Flask, render_template, request, redirect, url_for, session, flash,g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = "supersecretkey"
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

# Initialize DB and create example users with hashed passwords
with app.app_context():
    db.drop_all()
    db.create_all()

    db.session.add(User(username="example", password=generate_password_hash("abc")))
    db.session.add(User(username="example2", password=generate_password_hash("123")))
    db.session.add(User(username="admin", password=generate_password_hash("abc")))
    db.session.commit()

# Admin-only implementation
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in to view this page.", "warning")
            return redirect(url_for("login"))

        user = db.session.get(User, user_id)
        if not user or user.username != "admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("index"))

        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("login"))

        user = db.session.scalar(db.select(User).filter_by(username=username))
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Logged in successfully!", "success")
            if user.username == "admin":
                return redirect(url_for("users"))
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Both fields are required.", "warning")
            return redirect(url_for("add_user"))

        if db.session.scalar(db.select(User).filter_by(username=username)):
            flash("Username already exists.", "danger")
            return redirect(url_for("add_user"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!", "success")
        return redirect(url_for("users"))

    return render_template("add_user.html")

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route('/users')
@admin_required
def users():
    users = db.session.scalars(db.select(User)).all()
    return render_template("users.html", users=users)

@app.route('/about')
def about():
    return render_template("about.html")


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in to view your profile.", "warning")
        return redirect(url_for("login"))
    
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


@app.context_processor
def inject_current_user():
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
    return dict(current_user=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)



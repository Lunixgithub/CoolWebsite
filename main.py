from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, foreign, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = "supersecretkey"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)


# User database to implement several users
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()


# Post database to implement several posts
class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(backref="posts")


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
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Both fields are required.", "warning")
            return redirect(url_for("register"))

        if db.session.scalar(db.select(User).filter_by(username=username)):
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/users")
@admin_required
def users():
    users = db.session.scalars(db.select(User)).all()
    return render_template("users.html", users=users)


@app.route("/about")
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


@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to create a post.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required.", "warning")
            return redirect(url_for("create_post"))

        post = Post(title=title, content=content, author_id=user_id)
        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("posts"))

    return render_template("create_post.html")


@app.route("/posts")
def posts():
    posts = db.session.scalars(db.select(Post)).all()
    return render_template("posts.html", posts=posts)


@app.context_processor
def inject_current_user():
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
    return dict(current_user=user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", debug=True, port=81)

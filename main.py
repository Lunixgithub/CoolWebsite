from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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

with app.app_context():
    db.drop_all()
    db.create_all()

    db.session.add(User(username="example", password="abc"))
    db.session.add(User(username="example2", password="123"))
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

from flask import request, redirect, url_for, session, flash

@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Check for empty fields
        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("login"))

        # searches for login data in databae
        user = db.session.scalar(
            db.select(User).filter_by(username=username, password=password)
        )

        if user:
            session["user_id"] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route('/users')
def list_users():
    users = db.session.scalars(db.select(User)).all()
    return render_template("users.html", users=users)

if __name__ == "__main__":
   app.run(host= "0.0.0.0", debug=True, port=80)

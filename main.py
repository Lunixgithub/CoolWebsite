from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

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

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/users')
def list_users():
    users = db.session.scalars(db.select(User)).all()
    return render_template("users.html", users=users)

if __name__ == "__main__":
   app.run(host= "0.0.0.0", debug=True, port=80)

from flask import Flask, request, jsonify, session, flash, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
import time
import json
import datetime

key = json.loads(open("../secrets/porchjokes.json").read())["key"]


app = Flask(__name__)
app.config.update({
    'SECRET_KEY': key
})

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{un}:{pw}@{sv}/{db}".format(
    un="main",
    pw="punishment",
    sv="localhost",
    db="porchjokes"
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Joke(db.Model):

    __tablename__ = "jokes"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    title = db.Column(db.String(160000))
    joke = db.Column(db.String(160000))
    ip = db.Column(db.String(160000))
    pin = db.Column(db.Integer)
    date = db.Column(db.String(160000))
    time = db.Column(db.String(160000))

    def __repr__(self):
        return str(self.id)

@app.route("/")
def index():
    jokes = Joke.query.order_by(Joke.id.desc()).all()
    p_jokes = Joke.query.filter_by(pin="1").all()
    return render_template("index.html", p_jokes=p_jokes, jokes=jokes)


@app.route("/new_joke", methods=["GET", "POST"])
def new_joke():
    if request.method == "POST":
        try:
            session["last"]

        except:
            session["last"] = 0

        toFlash = []

        currTime = time.time()
        last = session["last"]
        
        if currTime - last >= 60 and len(request.form["username"]) <= 50 and len(request.form["title"]) <= 100 and len(request.form["joke"]) <= 600:
            session["last"] = time.time()
            info = str(datetime.datetime.now()).split()
            
            date = info[0].split("-")
            year, month, day = date[0], date[1], date[2]

            t = ":".join(info[1].split(":")[:2])
            
            submittedJoke = Joke(
                username=request.form["username"],
                title=request.form["title"],
                joke=request.form["joke"],
                ip=str(request.environ.get("HTTP_X_REAL_IP", request.remote_addr)),
                date="{}/{}/{}".format(month, day, year),
                time=str(t)
            )
            db.session.add(submittedJoke)
            db.session.commit()
            
        if currTime - last < 60:
            toFlash.append("Please wait {} seconds before you try again".format(int(500-last)))

        if len(request.form["username"]) > 50:
            toFlash.append("You need less than 50 characters for your username. Consider removing {} characters from your username.".format(50-len(request.form["username"])))

        if len(request.form["title"]) > 100:
            toFlash.append("You need less than 100 characters for your title. Consider removing {} characters from your title.".format(100-len(request.form["title"])))

        if len(request.form["joke"]) > 600:
            toFlash.append("You need less than 600 characters for your joke. Consider removing {} characters from your joke.".format(600-len(request.form["joke"])))

        if len(toFlash) > 0:
            flash(toFlash)
            return redirect("/new_joke")
        else:
            return redirect("/")

    else:
        return render_template("new_joke.html")

app.run(host="127.0.0.1", port=5050)







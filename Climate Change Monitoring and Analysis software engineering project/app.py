from flask import Flask, render_template, request, redirect,session, jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_login import logout_user, login_user, login_required, LoginManager, current_user
import bcrypt 
import pickle
import numpy as np
import requests


app=Flask(__name__)
clf = pickle.load(open("model_trail.pkl","rb"))   

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key="toplevelsecret"

db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False) 

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode("utf-8"))
    
with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        new_user = User(name=name, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/home')
    return render_template('register.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = user.username
            return redirect('/dashboard')
        else:
            return render_template("login.html", error="Invalid User")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if session['username']:
        return render_template("dashboard.html")
    return render_template("home.html")

@app.route('/model', methods=['GET','POST'])
def model():
    if session['username']:
        return render_template("model.html")
    return render_template("login.html")

@app.route("/prediction", methods=['POST'])
def prediction():
    temp = float(request.form.get("temp"))
    humidity = float(request.form.get("humidity"))
    wind = float(request.form.get("wind"))
    Visibility = float(request.form.get("Visibility"))
    

    #prediction
    result = clf.predict([[temp, humidity, wind, Visibility]])
    result= str(result[0])
    return render_template("model.html",result=result)
    # return [tempMax, tempMin, wind]

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect("/home")

@app.route('/index')
def index():
    # session.pop('username',None)
    # if session['username']:
    return render_template("index.html")
    # return redirect("/login")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")

if __name__ == '__main__':
    app.run(debug=True)
from datetime import date
from threading import local
from flask import Flask,request, url_for, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
with open('E:\VS\\templates\\config.json','r') as c:
    params=json.load(c)["params"]

local_server=True
new=Flask(__name__,  template_folder='E:\VS\\templates',static_folder='E:\VS\\static')
new.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail=Mail(new)
if(local_server):
    new.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    new.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(new)
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    phone_num = db.Column(db.Integer, nullable=False)
    msg = db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(6), nullable=True)
    email = db.Column(db.String(40), nullable=False)
class Transactions(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    send_name = db.Column(db.String(80), nullable=False)
    receive_name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(80))

class Customers(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Integer, nullable=False)    

@new.route("/")
def Homepage():
    return render_template('index.html',params=params)
@new.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name ,sender = email,recipients = [params['gmail-user']],body = message + "\n" + phone)           
    return render_template('contact.html',params=params )
@new.route("/About2")
def About2():
    return render_template('about1.html', params=params)
@new.route('/user/', methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        result = Customers.query.all()
        print(result)
        return render_template('user.html', result=result,params=params)


# to transfer amount to another customer
@new.route('/transactions/', methods=['GET', 'POST'])
def transactions():
    trans = Customers.query.all()
    if request.method == 'POST':
        sender = request.form.get('sname')
        receiver = request.form.get('rname')
        amount = request.form.get('balance')
        entry = Transactions(send_name=sender, receive_name=receiver, amount=amount, date=datetime.now())
        if receiver != sender:
            edited = db.session.query(Customers).filter_by(email=receiver).one()
            edited.balance += int(amount)
            edited3 = db.session.query(Customers).filter_by(email=sender).one()

            # if balance is greater than amount to be transferred only then transaction occurs
            if edited3.balance >= int(amount):
                edited3.balance -= int(amount)
                db.session.add(entry)
                db.session.commit()
                result = Transactions.query.all()
                print(result)
                return render_template('transhist.html', result=result,params=params)
    return render_template('transactions.html', trans=trans,params=params)


@new.route('/adduser/', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        cname = request.form.get('name')
        cemail = request.form.get('email')
        cbalance = request.form.get('balance')
        entry = Customers( name=cname, email=cemail, balance=cbalance)
        if(cname!= "" or cemail!= "" or cbalance!=""):
            db.session.add(entry)
            db.session.commit()
            res = Customers.query.all()
            return render_template('user.html', result=res,params=params)
    return render_template('adduser.html',params=params)


@new.route('/transhist/', methods=['GET', 'POST'])
def mers():
    if request.method == 'GET':
        result = Transactions.query.all()
        print(result)
        return render_template('transhist.html', result=result,params=params)


new.run(debug=True, port=9000) 
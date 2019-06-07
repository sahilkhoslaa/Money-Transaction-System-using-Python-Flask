# importing necessary libraries
from flask import Flask, session, url_for, render_template, request, redirect
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
import datetime
import time
import os

# app configuration FLASK
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Mongo DB - Flask Configuration
# Visit https://mlab.com/ which provides free database hosting
# upto 500 MB
app.config['MONGO_DBNAME'] = 'nknbanks'
app.config['MONGO_URI'] = 'mongodb://nikhilkhosla:nikhil123@ds151840.mlab.com:51840/nkbanks'

mongo = PyMongo(app)

# Dictionary for caching details of the logged in users
# (optimizes the database calls)
logged_users = {}

# function that refreshes transactions whenever a url is hit.
def refresh_transactions(id):
    transactions = mongo.db.transactions
    query_trans = transactions.find({"transfer_from": id}).sort("timestamp", -1)

    trans = []
    for i in range(0, query_trans.count()):
        trans.append(query_trans.next())
        if i >= 9:
            break
    return trans

# function to return timestamp
def get_timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st

# function that checks whether user is authenticated or not.
def authenticate():
    if 'user' in session:
        logged_users[session['user']]["trans"] = refresh_transactions(ObjectId(session['user']))
        return logged_users[session['user']]
    return None

# MAIN PAGE
@app.route('/index', methods=['GET', 'POST'])
def index():
    authorize = authenticate()
    if authorize is not None:
        return render_template('index.html', data=authorize)
    else:
        return redirect(url_for('login'))

# LOGIN PAGE
@app.route('/login', methods=['GET'])
def login():
    authorize = authenticate()
    if authorize is not None:
        redirect(url_for('index'))
    else:
        return render_template('login.html')

# REGISTER PAGE (not a requirement)
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

# WITHDRAW PAGE
@app.route('/withdraw', methods=['GET'])
def withdraw():
    authorize = authenticate()
    if authorize is not None:
        return render_template('withdraw.html', data=authorize)
    else:
        return redirect(url_for('login'))

# INVOICE PAGE
@app.route('/invoice_withdraw', methods=['POST'])
def invoice_withdraw():
    authorize = authenticate()
    if authorize is not None:
        authorize["account_balance"] = str(int(authorize["account_balance"]) - int(request.form["amount"]))

        user = mongo.db.users
        user.save(authorize)

        transaction = mongo.db.transactions

        trans = {"timestamp": get_timestamp(),
                 "type": "Withdraw Cash",
                 "amount": str(request.form["amount"]),
                 "transfer_from": authorize["_id"],
                 "transfer_to": authorize["_id"]}

        transaction.insert_one(trans)
        authorize["trans"] = trans
        logged_users["account_balance"] = authorize["account_balance"]
        return render_template('invoice.html', data=authorize)
    else:
        return redirect(url_for('login'))

# TRANSFER PAGE
@app.route('/transfer', methods=['GET','POST'])
def transfer():
    authorize = authenticate()
    if authorize is not None:
        return render_template('transfer.html', data=authorize)
    else:
        return redirect(url_for('login'))

# CHANGE PASSWORD PAGE
@app.route('/changepassword', methods=['GET'])
def changepassword():
    authorize = authenticate()
    if authorize is not None:
        return render_template('changepassword.html',data=authorize)
    else:
        return redirect(url_for('login'))

# API - CHANGE PASSWORD
@app.route('/api/changepassword', methods=['POST'])
def changepswd():
    authorize = authenticate()
    users = mongo.db.users

    if authorize is not None:
        authorize["password"] = request.form["newpassword"]
        users.save(authorize)

        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

# INVOICE TRANSFER PAGE
@app.route('/invoice_transfer', methods=['POST'])
def invoice_transfer():
    authorize = authenticate()
    if authorize is not None:
        print(authorize)
        users = mongo.db.users
        transaction = mongo.db.transactions

        find_account = users.find_one({"_id": ObjectId(request.form["account_id"])})
        if find_account is not None:
            find_account["account_balance"] = str(int(find_account["account_balance"]) + int(request.form["amount"]))
            authorize["account_balance"] = str(int(authorize["account_balance"]) - int(request.form["amount"]))
            users.save(find_account)
            users.save(authorize)

            trans = {"timestamp": get_timestamp(),
                     "type": "Transfer Cash",
                     "amount": str(request.form["amount"]),
                     "transfer_from": authorize["_id"],
                     "transfer_to": find_account["_id"]}

            transaction.insert_one(trans)

            authorize["trans"] = trans
            logged_users["account_balance"] = authorize["account_balance"]
            return render_template('invoice.html',data=authorize)
        else:
            # user not found
            return render_template('404.html', msg="No such User Exists")
    else:
        return redirect(url_for('login'))

# MINI STATEMENT OF A TRANSACTION
@app.route('/invoice_mini_statement/<string:id>',methods=['GET'])
def get_mini_statement(id):
    authorize = authenticate()

    if authorize is not None:
        transactions = mongo.db.transactions
        transaction = transactions.find_one({"_id" : ObjectId(id)})
        print(transaction)

        trans = {"timestamp": transaction["timestamp"],
                 "type": transaction["type"],
                 "amount": transaction["amount"],
                 "transfer_from": transaction["transfer_from"],
                 "transfer_to": transaction["transfer_to"]}
        authorize["trans"] = trans

        return render_template('invoice.html',data=authorize)
    else:
        return render_template('404.html', msg = "Some Error Occured : Check id of the transaction")

# API - LOGIN
@app.route('/api/login', methods=['POST'])
def authorize():
    username = request.form['username']
    password = request.form['password']

    users = mongo.db.users

    query = users.find_one({
        "username": username,
        "password": password
    })

    if query is not None:
        session['user'] = str(query["_id"])
        query["trans"] = refresh_transactions(query["_id"])
        logged_users[str(query["_id"])] = query

        return redirect(url_for('index'))
    else:
        return render_template('404.html', msg = "No Such User Exists")

# API - LOGOUT
@app.route('/api/logout',methods=['GET', 'POST'])
def logout():
    logged_users.pop(session['user'])
    for key in list(session):
        session.pop(key)
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
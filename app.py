from flask import Flask, render_template, url_for, request, session, redirect
from datetime import datetime
import pymongo
import bcrypt
import json

app = Flask(__name__)
app.secret_key = 'secret'

connection = pymongo.MongoClient('ds131320.mlab.com', 31320)
mongo = connection['moola']
mongo.authenticate('moola_user', 'th2017')

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('loggedin'))
    return render_template('login.html')

@app.route('/loggedin', methods=['POST', 'GET'])
def loggedin():
    if request.method == 'POST':
        balance = mongo.db.users.distinct('balance', {'username' : session['username']})
        ttype = request.form['transtype']
        date = request.form['date'] 
        description = request.form['message']
        category = request.form['cat']
        if ttype == 'deposit':
            amount = int(request.form['amt'])
        else:
            amount = -1 * int(request.form['amt'])
        mongo.db.users.find_one_and_update({'username' : session['username']},
            { '$push' : {'transactions' : [ttype, date, description, category, amount]}})
        mongo.db.users.find_one_and_update({'username' : session['username']},
            { '$inc' : {'balance' : amount }})
    transactions = mongo.db.users.distinct('transactions', {'username' : session['username']})
    with open("static/json/transactions.JSON", 'w') as outfile:
        json.dump(transactions, outfile)
    return render_template('loggedin.html', balance = mongo.db.users.distinct('balance', {'username' : session['username']})) 

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('logout.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username' : request.form['username']})

    if login_user:
        #hashed = request.form['pass'].encode('utf-8')
        #if bcrypt.hashpw(hashed, login_user['password']) == login_user['password']:
        if request.form['pass'] == login_user['password']: 
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Invalid username/password combination'

#################################################################

@app.route('/home')
def home():
	return render_template(
		'home.html',
		title='Home Page',
		year=datetime.now().year,
	)

@app.route('/personal')
def personal():
	return render_template(
		'personal.html',
		title='Personal Page',
		year=datetime.now().year,
	)

@app.route('/global')
def global_():
	return render_template(
		'global.html',
		title='Global Page',
		year=datetime.now().year,
	)

 
if __name__ == '__main__':
	app.run()

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
        if 'deposit' in request.form:
            mongo.db.users.find_one_and_update({'username' : session['username']},
                { '$inc' : {'balance' : int(request.form['damt'])}})
            depos = mongo.db.users.distinct('deposits', {'username' : session['username']})
            check = False
            for d in depos:
                if d[0] == request.form['ddate']:
                    d[1] = d[1] + int(request.form['damt'])
                    check = True
            if check==False:
                mong o.db.users.find_one_and_update({'username' : session['username']},
                    { '$push' : {'deposits' : [request.form['ddate'], int(request.form['damt'])] }})
            else:
                mongo.db.users.find_one_and_update({'username' : session['username']},
                    { '$set' : {'deposits' : depos}})
        if 'withdrawal' in request.form:
            if balance[0] - int(request.form['wamt']) < 0:
                return "Withdrawal amount is too much!"
            mongo.db.users.find_one_and_update({'username' : session['username']},
                { '$inc' : {'balance' : -1 * int(request.form['wamt'])}})
            wdraw = mongo.db.users.distinct('withdrawals', {'username' : session['username']})
            check = False
            for w in wdraw:
                if w[0] == request.form['wdate']:
                    w[1] = w[1] + int(request.form['wamt'])
                    check = True
            if check == False:
                mongo.db.users.find_one_and_update({'username' : session['username']},
                    {'$push' : {'withdrawals' : [request.form['wdate'], int(request.form['wamt'])] }})
            else:
                mongo.db.users.find_one_and_update({'username' : session['username']},
                    { '$set' : {'withdrawals' : wdraw }})
    wdraw = mongo.db.users.distinct('withdrawals', {'username' : session['username']})
    for w in wdraw:
        w[0] = (((datetime.strptime(w[0], '%Y-%m-%d'))-datetime(1970,1,1)).total_seconds()) * 1000
    with open("static/json/withdrawals.JSON", 'w') as outfile:
        json.dump(wdraw, outfile)
    depos = mongo.db.users.distinct('deposits', {'username' : session['username']})
    for d in depos:
        d[0] = (((datetime.strptime(d[0], '%Y-%m-%d'))-datetime(1970,1,1)).total_seconds()) * 1000
    with open("static/json/deposits.JSON", 'w') as outfile:
        json.dump(depos, outfile)
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

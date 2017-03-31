from flask import Flask, render_template, url_for, request, session, redirect
from datetime import datetime
import pymongo
import bcrypt
import json

app = Flask(__name__)

connection = pymongo.MongoClient('ds131320.mlab.com', 31320)
mongo = connection['moola']
mongo.authenticate('moola_user', 'th2017')


@app.route('/login', methods=['GET', 'POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username' : request.form['username']})
    if login_user:
        if request.form['pass'] == login_user['password']: 
            session['username'] = request.form['username']
            return redirect(url_for('login.html'))
    return 'Invalid username/password combination'



@app.route('/')
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

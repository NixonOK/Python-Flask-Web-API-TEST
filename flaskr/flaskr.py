# all the imports
import os
import sqlite3
import random
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='nixon',
    PASSWORD='123'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/show_entries', methods=['GET', 'POST'])
def show_entries():
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('''select * from entries where phone = ?''', (request.form['phone_search'],))
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries)
    else:
        return render_template('show_entries.html', entries=())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into entries (name, phone, verification_code, password) values (?, ?, ?, ?)',
                   [request.form['username_reg'], request.form['phone_reg'], 1111, request.form['password_reg']])
        db.commit()
        flash('Successfully Registered')
        return render_template('login.html')
    else:
        error = 'Sign Up please!'

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    error = None
    if request.method == 'POST':
        usrname = request.form['username']
        cur = db.execute('''select * from entries where name = ?''', (usrname,)).fetchall()
        for c in cur:
            if usrname != c["name"]:
                error = 'Invalid Username'
            elif request.form['password'] != app.config['PASSWORD']:
                error = 'Invalid password'
            else:
                rand = random.randrange(1000, 9999)
                db = get_db()
                usrname = request.form['username']
                flash(usrname)
                db.execute('''update entries set verification_code = ? where name = ?''', (rand, usrname))
                db.commit()
                flash('Code: %d' % rand)
                return redirect(url_for('verify'))
            flash('No account found, Please sign-up')
    return render_template('login.html', error=error)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    db = get_db()

    error = None
    if request.method == 'POST':
        usrname = request.form['username1']

        cur = db.execute('''select * from entries where name = ?''', (usrname,)).fetchall()
        for c in cur:
            flash('%d' % c["verification_code"])
            if usrname != c["name"]:
                error = 'Invalid Username'
            elif int(request.form['verificationCode1']) != c["verification_code"]:
                error = 'Invalid Verification Code'
            else:
                session['logged_in'] = True
                flash('You were logged in')
                return redirect(url_for('show_entries'))

    return render_template('verify.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))
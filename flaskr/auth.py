import functools

from markupsafe import escape
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, session

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

auth = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    functools.wraps(view)

    def user_is_available(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        view(**kwargs)
    return user_is_available


@auth.before_app_request
def get_logged_in_user():
    user_id = session.pop('user_id', None)

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(f'SELECT 1 FROM user where id = ?',
                            (user_id,)).fetchone()


@auth.route('register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get data, validate , hash , password, insert in db, flash, add error
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        error = None

        if username is None or password is None or email is None:
            error = 'All fields are required'

        if error is None:
            db = get_db()
            hashed_password = generate_password_hash(password=password)

            try:
                db.execute(f'insert into user (username, password, email) values (?,?,?)',
                           (username, hashed_password, email))
                db.commit()
            except db.IntegrityError:
                error = f'User {username} is already registered'
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')


@auth.route('login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        db = get_db()

        if email is None or password is None:
            error = 'All fields required'
        else:
            user = db.execute(
                'SELECT * from user WHERE email = ?', (email,)).fetchone()

            if user is None:
                error = 'credentials are invalid'

            elif check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['id']
                flash(f'{user["username"]} logged in successfully')
                return redirect(url_for('index'))
            else:
                error = 'credentials are invalid '
        flash(error)
    return render_template('auth/login.html')


@auth.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

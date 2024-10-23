import functools

from markupsafe import escape
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

auth = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def user_is_available(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return user_is_available


@auth.before_app_request
def get_logged_in_user():
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(f'SELECT * FROM user where id = ?',
                            (user_id,)).fetchone()
        print('checkin gg user...', g.user['first_name'])


@auth.route('register', methods=['GET', 'POST'])
def register():
    departmentOpts = ('DEV', 'SUPPORT', 'MARKETING', 'HR')
    if request.method == 'POST':
        # get data, validate , hash , password, insert in db, flash, add error
        print('request form...', request.form)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        department = request.form['department']
        is_admin = request.form['is_admin']
        password = request.form['password']
        email = request.form['email']
        error = None

        if first_name is None or password is None or email is None:
            error = 'All fields are required'

        if department not in departmentOpts:
            error = 'Department provided is unknown'

        if error is None:
            db = get_db()
            hashed_password = generate_password_hash(password=password)

            try:
                db.execute(f'insert into user (first_name,last_name,date_of_birth,department,is_admin, password, email) values (?,?,?,?, ?, ?, ?)',
                           (first_name, last_name, date_of_birth, department, is_admin, hashed_password, email))
                db.commit()
            except db.IntegrityError:
                error = f'User {first_name} is already registered'
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html', departmentOpts=departmentOpts)


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
                'SELECT email, first_name, last_name, date_of_birth, is_admin, department from user WHERE email = ?', (email,)).fetchone()

            if user is None:
                error = 'credentials are invalid'

            elif check_password_hash(user['password'], password):
                session.clear()
                session.permanent = True
                session['user_id'] = user['id']
                flash(f'{user["first_name"]} logged in successfully')
                return redirect(url_for('index'))
            else:
                error = 'credentials are invalid '
        flash(error)
    return render_template('auth/login.html')


@auth.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

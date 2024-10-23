from flask import (Blueprint, render_template, redirect, request, url_for)

from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

post = Blueprint('post', __name__)


@post.get('/')
@login_required
def index():
    db = get_db()
    users_with_post_count = db.execute('''SELECT u.id,email,department, last_logged_in, is_admin,first_name, last_name, date_of_birth, COUNT(p.id) as user_posts FROM user u
                       LEFT JOIN post p on u.id = p.author_id 
                        GROUP BY u.id,email,department, last_logged_in, is_admin''').fetchall()
    user_count = db.execute('SELECT count(*) FROM user').fetchone()[0]
    posts = db.execute(''' SELECT COUNT(*) FROM post''').fetchone()[0]

    print('dashboar', users_with_post_count, posts)
    return render_template('post/index.html', posts=posts, users=users_with_post_count, user_count=user_count)


@post.route('/users')
@login_required
def create_user():
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
                db.execute(f'INSERT INTO user (first_name,last_name,date_of_birth,department,is_admin, password, email) values (?,?,?,?, ?, ?, ?)',
                           (first_name, last_name, date_of_birth, department, is_admin, hashed_password, email))
                db.commit()
            except db.IntegrityError:
                error = f'User {first_name} is already registered'
            else:
                flash('User created successfully')
        else:
            flash(error)
    return render_template('post/create.html')


@post.delete('/users/<int:user>')
@login_required
def delete_user():
    user_id = request.args['user']
    db = get_db()
    error = None
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id)).fetchone()

    if not user:
        error = 'User not found'
    else:
        try:
            db.execute('DELETE FROM user where id = ?', (user_id))
            db.commit()
        except:
            error = 'Delete failed'
        else:
            flash('User has been deleted succesfully')

    if error:
        flash(error)
    return render_template('post/index.html')


@post.route('/users/<int:user>', methods=['GET', 'PUT'])
@login_required
def update_user():
    user_id = request.args['user']
    db = get_db()
    error = None
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id)).fetchone()
    if method == 'PUT':

        if not user:
            error = 'User not found'
        updateStmt = ''
        insert_values = []
        for (name, val) in request.form:
            if name == 'id':
                continue
            updateStmt += f'{name} = ?,'
            insert_values.append(val)

        try:
            db.execute(f'''UPDATE user
                    SET {updateStmt[:-1]}
                    WHERE id = ?''', tuple(insert_values))
            db.commit()
        except:
            error = 'User update failed'
        else:
            flash('User has been updated successfully')

        if error:
            flash(error)

    if method == 'GET' and not user:
        return redirect(url_for('index'))

    return redirect(url_for('index', user=user))

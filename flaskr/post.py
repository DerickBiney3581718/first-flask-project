from flask import (Blueprint, render_template,
                   redirect, request, url_for, flash, g)

from werkzeug.security import generate_password_hash
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

post = Blueprint('post', __name__)

departmentOpts = ('DEV', 'SUPPORT', 'MARKETING', 'HR')


@post.get('/')
@login_required
def index():
    db = get_db()
    users_with_post_count = db.execute('''SELECT u.id,email,department, last_logged_in, is_admin,first_name, last_name, date_of_birth, COUNT(p.id) as user_posts FROM user u
    LEFT JOIN post p on u.id = p.author_id 
    WHERE u.id <> ?
    GROUP BY u.id,email,department, last_logged_in, is_admin''', (str(g.user['id']))).fetchall()
    user_count = db.execute('SELECT count(*) FROM user').fetchone()[0]
    posts = db.execute(''' SELECT COUNT(*) FROM post''').fetchone()[0]

    return render_template('post/index.html', posts=posts, users=users_with_post_count, user_count=user_count)


@post.route('/users', methods=['POST', 'GET'])
@login_required
def create_user():
    if request.method == 'POST':
        # get data, validate , hash , password, insert in db, flash, add error
        print('request form...', request.form)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        department = request.form['department']
        is_admin = request.form['is_admin']
        password = 'default'
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
                return redirect(url_for('index'))
        else:
            flash(error)
    return render_template('post/create.html', departmentOpts=departmentOpts)


@post.route('/users/<user>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(user):

    user_id = user
    db = get_db()
    error = None
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id)).fetchone()

    if not user:
        error = 'User not found'
    if request.method == 'POST':
        try:
            db.execute('DELETE FROM user where id = ?', (user_id))
            db.commit()
        except:
            error = 'Delete failed'
        else:
            flash(
                f"User {user['last_name']} {user['first_name']} has been deleted succesfully")

        if error:
            flash(error)
        return redirect(url_for('index'))

    return render_template('post/delete.html', u=user)


@post.route('/users/<user>', methods=['GET', 'POST'])
@login_required
def update_user(user):
    user_id = user
    db = get_db()
    error = None
    print('the user id we want', user)
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id)).fetchone()

    if request.method == 'POST':

        if not user:
            error = 'User not found'
        else:
            updateStmt = ''
            insert_values = []

            form_data = request.form
            for (name, val) in form_data.items():
                if name == 'id':
                    user_id = val
                    continue
                updateStmt += f'{name} = ?,'
                insert_values.append(val)
            else:
                insert_values.append(user_id)

            print('insert items', insert_values)
            try:
                user = db.execute(f'''UPDATE user
                        SET {updateStmt[:-1]}
                        WHERE id = ?''', tuple(insert_values))
                print('lsdj', user)
                db.commit()
            except:
                error = 'User update failed'
            else:
                flash('User has been updated successfully')

        if error:
            flash(error)

    if request.method == 'GET' and not user:
        flash('User not found')
        return redirect(url_for('index'))

    return render_template('post/update.html', u=user, departmentOpts=departmentOpts)


@post.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    db = get_db()
    error = None
    user_id = str(g.user['id'])

    user = db.execute('SELECT * FROM user WHERE id = ?',
                      (user_id)).fetchone()

    if request.method == 'POST':

        if not user:
            error = 'User not found'
        else:
            updateStmt = ''
            insert_values = []

            form_data = request.form
            for (name, val) in form_data.items():
                if name == 'id':
                    user_id = val
                    continue
                updateStmt += f'{name} = ?,'
                insert_values.append(val)
            else:
                insert_values.append(user_id)

            print('insert items', insert_values)
            try:
                print('b4')
                db.execute(f'''UPDATE user
                        SET {updateStmt[:-1]}
                        WHERE id = ?''', tuple(insert_values))
                print('lsss', user['first_name'])
                db.commit()
            except:
                error = 'User update failed'
            else:
                try:
                    user = db.execute('SELECT * FROM user WHERE id = ?', (insert_values[-1],)).fetchone()
                    flash('User has been updated successfully')
                except:
                    error = 'refresh the page'

        if error:
            flash(error)

    if request.method == 'GET' and not user:
        flash('User not found')

    return render_template('post/profile.html', u=user, departmentOpts=departmentOpts)

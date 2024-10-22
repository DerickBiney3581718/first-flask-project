import os
from flask import Flask, render_template
from .auth import auth


def create_app(test_config=None):
    # config folder is relative to instance folder
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )
    app.register_blueprint(auth)

    # add either test or app config
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app_db(app)

    @app.route('/dashboard')
    def index():
        return render_template('index.html')

    return app

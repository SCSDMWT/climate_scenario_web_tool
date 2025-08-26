from flask import Flask
from flask_static_digest import FlaskStaticDigest
from .config import Config

flask_static_digest = FlaskStaticDigest()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    with app.app_context():
        from . import routes
        from . import db
        from . import data

        flask_static_digest.init_app(app)
        db.init_app(app)
        data.init_data(app)

        return app

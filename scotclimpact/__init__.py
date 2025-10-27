from flask import Flask
from flask_static_digest import FlaskStaticDigest
from werkzeug.middleware.profiler import ProfilerMiddleware

from .config import Config

flask_static_digest = FlaskStaticDigest()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    if app.config['PROFILE']:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

    with app.app_context():
        from . import routes
        from . import postgres
        from . import db
        from . import data

        flask_static_digest.init_app(app)
        postgres.pgdb.init_app(app)
        db.init_app(app)
        data.init_data(app)

        return app

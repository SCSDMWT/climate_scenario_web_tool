from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#from flask_flatpages import FlatPages
from .config import Config

#pages = FlatPages()
#db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    with app.app_context():
        from . import routes
        from . import db
        db.init_app(app)
        #pages.init_app(app)
        return app

from flask import Flask
from app.extensions import db, migrate, dbm
from app import models
from config import Config


def create_app(config_object=Config):
    _app = Flask(__name__)
    _app.config.from_object(config_object)
    register_extensions(_app)
    return _app


def register_extensions(_app):
    db.init_app(_app)
    migrate.init_app(_app, db)
    dbm.init_db(db, models)
    # gm.init_dbm(dbm)


app = create_app()
from app import routes  # FIXME: ugly.

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "somebody-once-told-me"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_LIFETIME_SEC = 60 * 60 * 24 * 3
    RANDOM_BORDER = 2 ** 30
    ADMIN_SECRET = os.environ.get("ADMIN_SECRET") or "mad-hatters"

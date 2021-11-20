from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from app.game_manager import GameManager
from app.db_manager import DBManager

db = SQLAlchemy()
migrate = Migrate()
# gm = GameManager()
dbm: DBManager = DBManager()

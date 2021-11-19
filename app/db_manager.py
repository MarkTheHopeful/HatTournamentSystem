from exceptions.DBExceptions import *
import entities.tournament


def database_response(database_fun):
    def wrapped(*args, **kwargs):
        try:
            result = database_fun(*args, **kwargs)
        except DBException as e:
            # print("DB KNOWN::")
            # print(e)
            raise e
        except Exception as e:
            print("DB UNKNOWN::")
            print(e)
            raise DBException()
        return result

    return wrapped


class DBManager:
    db = None
    models = None

    def init_db(self, db, models):
        self.db = db
        self.models = models

    def is_ok(self):
        return self.db is not None and self.models is not None

    @database_response
    def get_tokens_by_user_id(self, user_id):
        return self.models.Token.query.filter_by(user_id=user_id).all()

    @database_response
    def get_user_id_by_username(self, username):
        return self.get_user_by_username(username).id

    @database_response
    def get_username_and_exptime_by_token(self, token):
        # print(token)
        tok = self.models.Token.query.filter_by(id=token).first()
        # print(tok)
        if tok is None:
            raise DBTokenNotFoundException()
        print(tok.owner.username, tok.expires_in)
        return tok.owner.username, tok.expires_in

    @database_response
    def delete_token(self, token):
        tok = self.models.Token.query.filter_by(id=token).first()
        if tok is not None:
            self.db.session.delete(tok)
            self.db.session.commit()

    @database_response
    def get_user_by_username(self, username):
        u = self.models.User.query.filter_by(username=username).first()
        if u is None:
            raise DBUserNotFoundException()
        return u

    @database_response
    def get_passhash_by_username(self, username):
        u = self.models.User.query.filter_by(username=username).first()
        if u is None:
            raise DBUserNotFoundException()
        return u.password_hash

    @database_response
    def insert_token_to_username(self, token_id, expires_in, username):
        u = self.models.User.query.filter_by(username=username).first()
        tok = self.models.Token(id=token_id, expires_in=expires_in, owner=u)
        self.db.session.add(tok)
        self.db.session.commit()

    @database_response
    def insert_user(self, user_obj, pass_hash):
        new_user = self.models.User(username=user_obj.username, password_hash=pass_hash)
        try:
            self.db.session.add(new_user)
            self.db.session.commit()
        except IntegrityError as e:
            raise DBUserAlreadyExistsException(message=e)

    @database_response
    def insert_tournament(self, tournament_obj, username):
        u = self.models.User.query.filter_by(username=username).first()
        new_tournament = self.models.Tournament(name=tournament_obj.name, owner=u)
        self.db.session.add(new_tournament)
        self.db.session.commit()

    @database_response
    def get_tournaments(self, username):
        u = self.models.User.query.filter_by(username=username).first()

        return [entities.tournament.Tournament(dbu=t).to_base_info_dict() for t in list(u.tournaments)]

    @database_response
    def clear_all_tables(self):
        self.db.drop_all()
        self.db.create_all()

    def is_user_exists(self, username):
        u = self.models.User.query.filter_by(username=username).first()
        if u is None:
            return False
        return True

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
    def insert_player(self, username, tournament_name, name_first, name_second):
        tournament = self.get_tournament(username, tournament_name)

        if self.is_player_in_table(name_first, tournament.id) or self.is_player_in_table(name_second, tournament.id):
            raise DBPlayerAlreadyExistsException()

        new_player = self.models.Player(name_first=name_first, name_second=name_second, tournament=tournament)
        try:
            self.db.session.add(new_player)
            self.db.session.commit()
        except IntegrityError as e:
            raise RuntimeError(e)  # FIXME: This state should never be reached!

    @database_response
    def delete_player(self, username, tournament_name, name_first, name_second):
        tournament = self.get_tournament(username, tournament_name)
        pair_to_delete = self.get_pair(name_first, name_second, tournament.id)
        if pair_to_delete is None:
            raise DBPairNotFoundException()
        self.db.session.delete(pair_to_delete)
        self.db.session.commit()

    @database_response
    def clear_all_tables(self):
        self.db.drop_all()
        self.db.create_all()

    def is_player_in_table(self, player_name, tournament_id):
        return self.models.Player.query.filter(((self.models.Player.tournament_id == tournament_id) & (
                (self.models.Player.name_first == player_name) |
                (self.models.Player.name_second == player_name)))).first() is not None

    def is_user_exists(self, username):
        u = self.models.User.query.filter_by(username=username).first()
        return not (u is None)

    def get_pair(self, name_first, name_second, tournament_id):
        return self.models.Player.query.filter(((self.models.Player.tournament_id == tournament_id) & (
                ((self.models.Player.name_first == name_first) & (self.models.Player.name_second == name_second)) |
                ((self.models.Player.name_first == name_second) & (self.models.Player.name_second == name_first)))
                                                )).first()

    def get_tournament(self, username, tournament_name):
        u = self.models.User.query.filter_by(username=username).first()
        tournament = self.models.Tournament.query.filter((
                (self.models.Tournament.user_id == u.id) & (self.models.Tournament.name == tournament_name))).first()
        if tournament is None:
            raise DBTournamentNotOwnedException()
        return tournament

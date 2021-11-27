from exceptions.DBExceptions import *
import entities.tournament
import entities.player
import entities.word
import entities.round


# FIXME: too many duplicated lines!

def database_response(database_fun):  # FIXME: Seems useless
    def wrapped(*args, **kwargs):
        try:
            result = database_fun(*args, **kwargs)
        except DBException as e:
            raise e
        except Exception as e:
            print("DB UNKNOWN::")  # FIXME: Possibly left here for some particular reason
            print(e)
            raise DBException(str(e))
        return result

    return wrapped


class DBManager:
    db = None
    models = None

    # BASE FUNCTIONS

    def init_db(self, db, models):
        self.db = db
        self.models = models

    def is_ok(self):
        return self.db is not None and self.models is not None

    # HELPERS FUNCTIONS
    # FIXME: creates lots of objects only to check whether they are in db. Too bad!

    def is_user_exists(self, username: str) -> bool:
        u = self.models.User.query.filter_by(username=username).first()
        return u is not None

    def get_user(self, username: str):  # Returns Not None User Object
        u = self.models.User.query.filter_by(username=username).first()
        if u is None:
            raise DBObjectNotFound("User")
        return u

    def is_token_exists(self, token):
        tok = self.models.Token.query.filter_by(id=token).first()
        return tok is not None

    def get_token(self, token):
        tok = self.models.Token.query.filter_by(id=token).first()
        if tok is None:
            raise DBObjectNotFound("Token")
        return tok

    def is_tournament_exists(self, username, tournament_name):
        u = self.get_user(username)
        t = self.models.Tournament.query.filter((
                (self.models.Tournament.user_id == u.id) & (self.models.Tournament.name == tournament_name))).first()
        return t is not None

    def get_tournament(self, username, tournament_name):
        u = self.get_user(username)
        t = self.models.Tournament.query.filter((
                (self.models.Tournament.user_id == u.id) & (self.models.Tournament.name == tournament_name))).first()
        if t is None:
            raise DBObjectNotFound("Tournament")
        return t

    def is_round_exists(self, username, tournament_name, round_name):
        t = self.get_tournament(username, tournament_name)
        r = self.models.Round.query.filter((self.models.Round.name == round_name) &
                                           (self.models.Round.tournament_id == t.id)).first()
        return r is not None

    def get_round(self, username, tournament_name, round_name):
        t = self.get_tournament(username, tournament_name)
        return self.models.Round.query.filter(
            (self.models.Round.name == round_name) & (self.models.Round.tournament_id == t.id)).first()

    def is_player_exists(self, username, tournament_name, player_name):
        return None  # FIXME: fuck up

    def is_player_in_table(self, player_name, tournament_id):
        return self.models.Player.query.filter(((self.models.Player.tournament_id == tournament_id) & (
                (self.models.Player.name_first == player_name) |
                (self.models.Player.name_second == player_name)))).first() is not None

    def get_pair(self, name_first, name_second, tournament_id):
        return self.models.Player.query.filter(((self.models.Player.tournament_id == tournament_id) & (
                ((self.models.Player.name_first == name_first) & (self.models.Player.name_second == name_second)) |
                ((self.models.Player.name_first == name_second) & (self.models.Player.name_second == name_first)))
                                                )).first()  # FIXME: this look awful!

    def is_word_in_table(self, word_text, tournament_id):
        return self.models.Word.query.filter((self.models.Word.text == word_text) & (
                self.models.Word.tournament_id == tournament_id)).first() is not None

    # DATABASE RESPONSES

    @database_response
    def insert_user(self, user_obj, pass_hash):
        new_user = self.models.User(username=user_obj.username, password_hash=pass_hash)
        try:
            self.db.session.add(new_user)
            self.db.session.commit()
        except IntegrityError:
            raise DBObjectAlreadyExists("User")

    @database_response
    def get_password_hash(self, username):
        u = self.get_user(username)
        return u.password_hash

    @database_response
    def get_username_and_exptime_by_token(self, token):
        tok = self.get_token(token)
        return tok.owner.username, tok.expires_in

    @database_response
    def insert_token(self, token_id, expires_in, username):
        u = self.get_user(username)
        tok = self.models.Token(id=token_id, expires_in=expires_in, owner=u)
        self.db.session.add(tok)
        self.db.session.commit()

    @database_response
    def delete_token(self, token):
        if not self.is_token_exists(token):
            return
        tok = self.get_token(token)
        self.db.session.delete(tok)
        self.db.session.commit()

    @database_response
    def insert_tournament(self, username, tournament_obj):
        u = self.get_user(username)
        if self.is_tournament_exists(username, tournament_obj.name):
            raise DBObjectAlreadyExists("Tournament")
        new_tournament = self.models.Tournament(name=tournament_obj.name, owner=u)
        self.db.session.add(new_tournament)
        self.db.session.commit()

    @database_response
    def get_tournaments(self, username):
        u = self.get_user(username)
        return [entities.tournament.Tournament(dbu=t).to_base_info_dict() for t in u.tournaments]

    @database_response
    def insert_round(self, username, tournament_name, round_name, round_difficulty):
        if self.is_round_exists(username, tournament_name, round_name):
            raise DBObjectAlreadyExists("Round")

        tournament = self.get_tournament(username, tournament_name)
        new_round = self.models.Round(name=round_name, difficulty=round_difficulty,
                                      tournament=tournament)
        self.db.session.add(new_round)

    @database_response
    def get_rounds(self, username, tournament_name):
        tournament = self.get_tournament(username, tournament_name)
        return [entities.round.Round(dbu=r).to_base_info_dict() for r in tournament.rounds]

    @database_response
    def delete_round(self, username, tournament_name, round_name):
        round_to_delete = self.get_round(username, tournament_name, round_name)
        self.db.session.delete(round_to_delete)
        self.db.session.commit()

    @database_response
    def insert_player(self, username, tournament_name, name_first, name_second):
        tournament = self.get_tournament(username, tournament_name)

        if self.is_player_in_table(name_first, tournament.id) or self.is_player_in_table(name_second, tournament.id):
            raise DBObjectAlreadyExists("Player")

        new_player = self.models.Player(name_first=name_first, name_second=name_second, tournament=tournament)
        try:
            self.db.session.add(new_player)
            self.db.session.commit()
        except IntegrityError as e:
            raise RuntimeError(e)  # FIXME: This state should never be reached! and how will this work?

    @database_response
    def get_players(self, username, tournament_name):
        tournament = self.get_tournament(username, tournament_name)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in tournament.players]

    @database_response
    def delete_player(self, username, tournament_name, name_first, name_second):
        tournament = self.get_tournament(username, tournament_name)
        pair_to_delete = self.get_pair(name_first, name_second, tournament.id)
        if pair_to_delete is None:
            raise DBObjectNotFound("Player")
        self.db.session.delete(pair_to_delete)
        self.db.session.commit()

    @database_response
    def insert_word(self, username, tournament_name, word_text, word_difficulty):
        tournament = self.get_tournament(username, tournament_name)

        if self.is_word_in_table(word_text, tournament.id):
            raise DBObjectAlreadyExists("Word")

        new_word = self.models.Word(text=word_text, difficulty=word_difficulty, tournament=tournament)
        try:
            self.db.session.add(new_word)
            self.db.session.commit()
        except IntegrityError as e:
            raise RuntimeError(e)  # FIXME: This state should never be reached!

    @database_response
    def get_words(self, username, tournament_name):
        tournament = self.get_tournament(username, tournament_name)
        return [entities.word.Word(dbu=w).to_base_info_dict() for w in tournament.words]

    @database_response
    def delete_word(self, username, tournament_name, word_text):
        tournament = self.get_tournament(username, tournament_name)
        word_to_delete = self.models.Word.query.filter_by(text=word_text, tournament_id=tournament.id).first()
        if word_to_delete is None:
            raise DBObjectNotFound("Word")
        self.db.session.delete(word_to_delete)
        self.db.session.commit()

    @database_response
    def add_pair_id_to_round(self, username, tournament_name, round_name, pair_id):
        tournament = self.get_tournament(username, tournament_name)
        round_obj = self.get_round(username, tournament_name, round_name)
        if round_obj is None:
            raise DBObjectNotFound("Round")
        player_obj = self.models.Player.query.filter_by(id=pair_id).first()
        if player_obj is None:
            raise DBObjectNotFound("Player")
        try:
            round_obj.players.append(player_obj)
            self.db.session.add(round_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise DBObjectAlreadyExists("Player in round")

    @database_response
    def get_players_in_round(self, username, tournament_name, round_name):
        tournament = self.get_tournament(username, tournament_name)
        round_obj = self.get_round(username, tournament_name, round_name)
        if round_obj is None:
            raise DBObjectNotFound("Round")
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in
                self.db.session.query(self.models.Round).filter_by(id=round_obj.id).first().players]

    @database_response
    def delete_player_from_round(self, username, tournament_name, round_name, pair_id):
        tournament = self.get_tournament(username, tournament_name)  # FIXME: Duplicated code!
        round_obj = self.get_round(username, tournament_name, round_name)
        if round_obj is None:
            raise DBObjectNotFound("Round")
        player_obj = self.models.Player.query.filter_by(id=pair_id).first()
        if player_obj is None:
            raise DBObjectNotFound("Player")
        try:
            round_obj.players.remove(player_obj)
            self.db.session.add(round_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise DBObjectNotFound("Player in round")

    @database_response
    def clear_all_tables(self):
        self.db.drop_all()
        self.db.create_all()

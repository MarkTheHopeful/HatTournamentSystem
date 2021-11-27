from exceptions.DBExceptions import *
import entities.tournament
import entities.player
import entities.word
import entities.round
from entities.subround import Subround as SubroundE  # FIXME: differs for weird reasons


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
            raise DBException(message=str(e))
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
        r = self.models.Round.query.filter(
            (self.models.Round.name == round_name) & (self.models.Round.tournament_id == t.id)).first()
        if r is None:
            raise DBObjectNotFound("Round")
        return r

    def is_player_exists(self, username, tournament_name, player_name):  # FIXME: will be changed, Player class changes
        t = self.get_tournament(username, tournament_name)
        p = self.models.Player.query.filter(((self.models.Player.tournament_id == t.id) & (
                (self.models.Player.name_first == player_name) |
                (self.models.Player.name_second == player_name)))).first()
        return p is not None

    def get_pair(self, username, tournament_name, name_first, name_second):  # FIXME: cringe
        t = self.get_tournament(username, tournament_name)
        p = self.models.Player.query.filter(((self.models.Player.tournament_id == t.id) & (
                ((self.models.Player.name_first == name_first) & (self.models.Player.name_second == name_second)) |
                ((self.models.Player.name_first == name_second) & (self.models.Player.name_second == name_first)))
                                             )).first()
        if p is None:
            raise DBObjectNotFound("Player")
        return p

    def get_pair_by_id(self, pair_id):  # FIXME: merge with previous using kwargs
        p = self.models.Player.query.filter_by(id=pair_id).first()
        if p is None:
            raise DBObjectNotFound("Player")
        return p

    def is_word_exists(self, username, tournament_name, word_text):
        t = self.get_tournament(username, tournament_name)
        w = self.models.Word.query.filter((self.models.Word.text == word_text) & (
                self.models.Word.tournament_id == t.id)).first()
        return w is not None

    def get_word(self, username, tournament_name, word_text):
        t = self.get_tournament(username, tournament_name)
        w = self.models.Word.query.filter((self.models.Word.text == word_text) & (
                self.models.Word.tournament_id == t.id)).first()
        if w is None:
            raise DBObjectNotFound("Word")
        return w

    def is_subround_exists(self, username, tournament_name, round_name, subround_name):
        r = self.get_round(username, tournament_name, round_name)
        s = self.models.Subround.query.filter((self.models.Subround.name == subround_name) & (
                self.models.Subround.round_id == r.id)).first()
        return s is not None

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
        return new_tournament.id

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
        self.db.session.commit()
        return new_round.id

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
        if (self.is_player_exists(username, tournament_name, name_first) or
                self.is_player_exists(username, tournament_name, name_second)):
            raise DBObjectAlreadyExists("Player")

        tournament = self.get_tournament(username, tournament_name)
        new_player = self.models.Player(name_first=name_first, name_second=name_second, tournament=tournament)
        self.db.session.add(new_player)
        self.db.session.commit()
        return new_player.id

    @database_response
    def get_players(self, username, tournament_name):
        tournament = self.get_tournament(username, tournament_name)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in tournament.players]

    @database_response
    def delete_player(self, username, tournament_name, name_first, name_second):
        pair_to_delete = self.get_pair(username, tournament_name, name_first, name_second)
        self.db.session.delete(pair_to_delete)
        self.db.session.commit()

    @database_response
    def insert_word(self, username, tournament_name, word_text, word_difficulty):

        if self.is_word_exists(username, tournament_name, word_text):
            raise DBObjectAlreadyExists("Word")

        tournament = self.get_tournament(username, tournament_name)
        new_word = self.models.Word(text=word_text, difficulty=word_difficulty, tournament=tournament)
        self.db.session.add(new_word)
        self.db.session.commit()
        return new_word.id

    @database_response
    def get_words(self, username, tournament_name):
        tournament = self.get_tournament(username, tournament_name)
        return [entities.word.Word(dbu=w).to_base_info_dict() for w in tournament.words]

    @database_response
    def delete_word(self, username, tournament_name, word_text):
        word_to_delete = self.get_word(username, tournament_name, word_text)
        self.db.session.delete(word_to_delete)
        self.db.session.commit()

    @database_response
    def add_pair_id_to_round(self, username, tournament_name, round_name, pair_id):
        round_obj = self.get_round(username, tournament_name, round_name)
        player_obj = self.get_pair_by_id(pair_id)
        try:  # FIXME: Find some better way to check
            round_obj.players.append(player_obj)
            self.db.session.add(round_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise DBObjectAlreadyExists("Player in round")

    @database_response
    def get_players_in_round(self, username, tournament_name, round_name):
        round_obj = self.get_round(username, tournament_name, round_name)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in
                self.db.session.query(self.models.Round).filter_by(id=round_obj.id).first().players]

    @database_response
    def delete_player_from_round(self, username, tournament_name, round_name, pair_id):
        round_obj = self.get_round(username, tournament_name, round_name)
        player_obj = self.get_pair_by_id(pair_id)
        try:
            round_obj.players.remove(player_obj)
            self.db.session.add(round_obj)
            self.db.session.commit()
        except StaleDataError as e:
            raise DBObjectNotFound("Player in round")

    @database_response
    def insert_subround(self, username, tournament_name, round_name, subround_name):
        if self.is_subround_exists(username, tournament_name, round_name, subround_name):
            raise DBObjectAlreadyExists("Subround")

        round_obj = self.get_round(username, tournament_name, round_name)
        new_subround = self.models.Subround(name=subround_name, round=round_obj)
        self.db.session.add(new_subround)
        self.db.session.commit()
        return new_subround.id

    @database_response
    def get_subrounds(self, username, tournament_name, round_name):
        round_obj = self.get_round(username, tournament_name, round_name)
        return [SubroundE(dbu=p).to_base_info_dict() for p in round_obj.subrounds]

    @database_response
    def clear_all_tables(self):
        self.db.drop_all()
        self.db.create_all()

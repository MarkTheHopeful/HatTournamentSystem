from typing import Tuple, Callable, Optional
from flask_sqlalchemy import SQLAlchemy

from exceptions import KnownException
from exceptions.UserExceptions import LogicGameSizeException, LogicPlayersDontMatch, ObjectNotFound, ObjectAlreadyExists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError
import entities.tournament
import entities.player
import entities.word
import entities.round
from collections import Counter
from datetime import datetime as DatetimeT
from entities.subround import Subround as SubroundE  # FIXME: differs for weird reasons

# FIXME: too many duplicated lines!
from utils.utils import gen_rand_key, shuffle_and_split_near_equal_parts


class DBException(KnownException):
    def __init__(self, code: int = 500, message: str = "Unknown DB error"):
        self.code = code
        self.message = message
        super().__init__(code, message)


def database_response(database_fun: Callable) -> Callable:  # FIXME: Seems useless
    def wrapped(*args, **kwargs):
        try:
            result = database_fun(*args, **kwargs)
        except KnownException as e:
            raise e
        except Exception as e:
            raise DBException(500, str(e))
        return result

    return wrapped


class DBManager:

    def __init__(self):
        self.db: Optional[SQLAlchemy] = None
        self.models = None

    # BASE FUNCTIONS

    def init_db(self, db: SQLAlchemy, models):
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
            raise ObjectNotFound("User")
        return u

    def is_token_exists(self, token: str):
        tok = self.models.Token.query.filter_by(id=token).first()
        return tok is not None

    def get_token(self, token: str):
        tok = self.models.Token.query.filter_by(id=token).first()
        if tok is None:
            raise ObjectNotFound("Token")
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
            raise ObjectNotFound("Tournament")
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
            raise ObjectNotFound("Round")
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
            raise ObjectNotFound("Player")
        return p

    def get_pair_by_id(self, pair_id):  # FIXME: merge with previous using kwargs
        p = self.models.Player.query.filter_by(id=pair_id).first()
        if p is None:
            raise ObjectNotFound("Player")
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
            raise ObjectNotFound("Word")
        return w

    def is_subround_exists(self, username, tournament_name, round_name, subround_name):
        r = self.get_round(username, tournament_name, round_name)
        s = self.models.Subround.query.filter((self.models.Subround.name == subround_name) & (
                self.models.Subround.round_id == r.id)).first()
        return s is not None

    def get_subround(self, username, tournament_name, round_name, subround_name):
        r = self.get_round(username, tournament_name, round_name)
        s = self.models.Subround.query.filter((self.models.Subround.name == subround_name) & (
                self.models.Subround.round_id == r.id)).first()
        if s is None:
            raise ObjectNotFound("Subround")
        return s

    def get_x_random_words_with_difficulty_y(self, username, tournament_name, amount, difficulty):
        t = self.get_tournament(username, tournament_name)
        words = self.models.Word.query.filter_by(tournament_id=t.id, difficulty=difficulty, subround_id=None).order_by(
            self.models.Word.random_seed).limit(amount).all()

        if len(words) < amount:
            raise ObjectNotFound("Not enough words")
        return words

    def link_words_with_subround(self, subround_obj, words_list):
        subround_obj.words.extend(words_list)
        self.db.session.add(subround_obj)
        self.db.session.commit()

    def is_game_exists(self, username, tournament_name, game_id):
        t = self.get_tournament(username, tournament_name)
        g = self.models.Game.query.filter_by(id=game_id).first()

        return g is not None and g.subround.round.tournament.id == t.id

    def get_game(self, username, tournament_name, game_id):
        t = self.get_tournament(username, tournament_name)
        g = self.models.Game.query.filter_by(id=game_id).first()

        if g is None or g.subround.round.tournament.id != t.id:
            raise ObjectNotFound("Game")

        return g

    def update_add_results_push_from_game(self, game_obj):
        subround_obj = game_obj.subround
        new_results = Counter(subround_obj.results) + game_obj.results
        subround_obj.results = new_results
        self.db.session.add(subround_obj)
        self.db.session.add(game_obj)
        self.db.session.commit()
        self.update_add_results_push_from_subround(subround_obj)

    def update_add_results_push_from_subround(self, subround_obj):
        round_obj = subround_obj.round  # FIXME: duplicated code.
        new_results = Counter(round_obj.results) + subround_obj.results
        round_obj.results = new_results
        self.db.session.add(subround_obj)
        self.db.session.add(round_obj)
        self.db.session.commit()

    def update_subtract_results_push_from_game(self, game_obj):
        subround_obj = game_obj.subround
        new_results = Counter(subround_obj.results) - game_obj.results
        subround_obj.results = new_results
        self.db.session.add(subround_obj)
        self.db.session.add(game_obj)
        self.db.session.commit()
        self.update_subtract_results_push_from_subround(subround_obj, game_obj)

    def update_subtract_results_push_from_subround(self, subround_obj, game_obj):
        round_obj = subround_obj.round
        new_results = Counter(round_obj.results) - game_obj.results
        round_obj.results = new_results
        self.db.session.add(subround_obj)
        self.db.session.add(round_obj)
        self.db.session.commit()

    # DATABASE RESPONSES

    @database_response
    def insert_user(self, user_obj, pass_hash: str):
        new_user = self.models.User(username=user_obj.username, password_hash=pass_hash)
        try:
            self.db.session.add(new_user)
            self.db.session.commit()
        except IntegrityError:
            raise ObjectAlreadyExists("User")

    @database_response
    def get_password_hash(self, username: str) -> str:
        user_obj = self.get_user(username)
        return user_obj.password_hash

    @database_response
    def get_username_and_exptime_by_token(self, token: str) -> Tuple[str, DatetimeT]:
        token_obj = self.get_token(token)
        return token_obj.owner.username, token_obj.expires_in

    @database_response
    def insert_token(self, token_id: str, expires_in: DatetimeT, username: str) -> None:
        user_obj = self.get_user(username)
        tok = self.models.Token(id=token_id, expires_in=expires_in, owner=user_obj)
        self.db.session.add(tok)
        self.db.session.commit()

    @database_response
    def delete_token(self, token: str) -> None:
        if not self.is_token_exists(token):
            return
        tok = self.get_token(token)
        self.db.session.delete(tok)
        self.db.session.commit()

    @database_response
    def insert_tournament(self, username, tournament_obj):
        user_obj = self.get_user(username)
        if self.is_tournament_exists(username, tournament_obj.name):
            raise ObjectAlreadyExists("Tournament")
        new_tournament = self.models.Tournament(name=tournament_obj.name, owner=user_obj)
        self.db.session.add(new_tournament)
        self.db.session.commit()
        return new_tournament.id

    @database_response
    def get_tournaments(self, username):
        u = self.get_user(username)
        return [entities.tournament.Tournament(dbu=t).to_base_info_dict() for t in u.tournaments]

    @database_response
    def insert_round(self, username, tournament_name, round_name):
        if self.is_round_exists(username, tournament_name, round_name):
            raise ObjectAlreadyExists("Round")

        tournament = self.get_tournament(username, tournament_name)
        new_round = self.models.Round(name=round_name,
                                      tournament=tournament, results=Counter())
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
            raise ObjectAlreadyExists("Player")

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
            raise ObjectAlreadyExists("Word")

        tournament = self.get_tournament(username, tournament_name)
        new_word = self.models.Word(text=word_text, difficulty=word_difficulty, tournament=tournament,
                                    random_seed=gen_rand_key())
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
            results = Counter(round_obj.results)
            results[pair_id] = 0
            round_obj.results = results
            self.db.session.add(round_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise ObjectAlreadyExists("Player in round")

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
            results = Counter(round_obj.results)
            del results[pair_id]
            round_obj.results = results
            self.db.session.add(round_obj)
            self.db.session.commit()
        except StaleDataError as e:
            raise ObjectNotFound("Player in round")

    @database_response
    def insert_subround(self, username, tournament_name, round_name, subround_name):
        if self.is_subround_exists(username, tournament_name, round_name, subround_name):
            raise ObjectAlreadyExists("Subround")

        round_obj = self.get_round(username, tournament_name, round_name)
        new_subround = self.models.Subround(name=subround_name, round=round_obj, results=Counter())
        self.db.session.add(new_subround)
        self.db.session.commit()
        return new_subround.id

    @database_response
    def get_subrounds(self, username, tournament_name, round_name):
        round_obj = self.get_round(username, tournament_name, round_name)
        return [SubroundE(dbu=p).to_base_info_dict() for p in round_obj.subrounds]

    @database_response
    def delete_subround(self, username, tournament_name, round_name, subround_name):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        self.db.session.delete(subround_obj)
        self.db.session.commit()

    @database_response
    def add_pair_id_to_subround(self, username, tournament_name, round_name, subround_name, pair_id):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        player_obj = self.get_pair_by_id(pair_id)
        try:  # FIXME: Find some better way to check
            subround_obj.players.append(player_obj)
            results = Counter(subround_obj.results)
            results[pair_id] = 0
            subround_obj.results = results
            self.db.session.add(subround_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise ObjectAlreadyExists("Player in subround")

    @database_response
    def get_players_in_subround(self, username, tournament_name, round_name, subround_name):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in
                self.db.session.query(self.models.Subround).filter_by(id=subround_obj.id).first().players]

    @database_response
    def delete_player_from_subround(self, username, tournament_name, round_name, subround_name, pair_id):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        player_obj = self.get_pair_by_id(pair_id)
        try:
            subround_obj.players.remove(player_obj)
            results = Counter(subround_obj.results)
            del results[pair_id]
            subround_obj.results = results
            self.db.session.add(subround_obj)
            self.db.session.commit()
        except StaleDataError as e:
            raise ObjectNotFound("Player in round")

    @database_response
    def add_x_words_of_diff_y_to_subround(self, username, tournament_name, round_name, subround_name, words_difficulty,
                                          words_amount):
        words = self.get_x_random_words_with_difficulty_y(username, tournament_name, words_amount, words_difficulty)
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        self.link_words_with_subround(subround_obj, words)

    @database_response
    def get_subround_words(self, username, tournament_name, round_name, subround_name):
        s = self.get_subround(username, tournament_name, round_name, subround_name)
        return [entities.word.Word(dbu=w).to_base_info_dict() for w in s.words]

    @database_response
    def split_subround_into_games(self, username, tournament_name, round_name, subround_name, games_amount):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        if subround_obj.games.count() > 0:
            raise ObjectAlreadyExists("Subround already split")
        if subround_obj.players.count() < 2 * games_amount:
            raise LogicGameSizeException()
        players_parts = shuffle_and_split_near_equal_parts(subround_obj.players.all(),
                                                           games_amount)  # FIXME: can be slow?
        for players_part in players_parts:
            results_counter = Counter([(p.id, 0) for p in players_part])
            new_game = self.models.Game(subround=subround_obj, results=results_counter, results_set=False)
            self.db.session.add(new_game)
            self.db.session.commit()
            for player in players_part:
                player.games.append(new_game)
                self.db.session.add(player)
                self.db.session.commit()
        final_ids = [game.id for game in subround_obj.games]
        return final_ids

    @database_response
    def get_games(self, username, tournament_name, round_name, subround_name):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        games_ids = [game.id for game in subround_obj.games]
        return games_ids

    @database_response
    def undo_split_subround_into_games(self, username, tournament_name, round_name, subround_name):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        if subround_obj.games.count() == 0:
            raise ObjectNotFound("Subround not split")
        for game in subround_obj.games:
            self.db.session.delete(game)  # I believe in cascade delete
        self.db.session.commit()

    @database_response
    def get_game_players(self, username, tournament_name, game_id):
        game_obj = self.get_game(username, tournament_name, game_id)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in game_obj.players]

    @database_response
    def set_game_result(self, username, tournament_name, game_id, result):
        game_obj = self.get_game(username, tournament_name, game_id)
        if game_obj.results_set:
            raise ObjectAlreadyExists("Game results")
        if result.keys() != set([p.id for p in game_obj.players]):
            raise LogicPlayersDontMatch()
        game_obj.results_set = True
        game_obj.results = result
        self.db.session.add(game_obj)
        self.db.session.commit()
        self.update_add_results_push_from_game(game_obj)

    @database_response
    def get_game_result(self, username, tournament_name, game_id):
        game_obj = self.get_game(username, tournament_name, game_id)
        if not game_obj.results_set:
            raise ObjectNotFound("Game results")
        return game_obj.results

    @database_response
    def delete_game_result(self, username, tournament_name, game_id):
        game_obj = self.get_game(username, tournament_name, game_id)
        if not game_obj.results_set:
            raise ObjectNotFound("Game results")
        self.update_subtract_results_push_from_game(game_obj)
        game_obj.results_set = False
        self.db.session.add(game_obj)
        self.db.session.commit()

    @database_response
    def get_subround_result(self, username, tournament_name, round_name, subround_name):
        subround_obj = self.get_subround(username, tournament_name, round_name, subround_name)
        if subround_obj.results is None:
            raise ObjectNotFound("Game results")
        return subround_obj.results

    @database_response
    def get_round_result(self, username, tournament_name, round_name):
        round_obj = self.get_round(username, tournament_name, round_name)
        if round_obj.results is None:
            raise ObjectNotFound("Game results")
        return round_obj.results

    @database_response
    def clear_all_tables(self):
        self.db.drop_all()
        self.db.create_all()

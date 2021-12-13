from typing import Tuple, Callable, Optional, List, Dict
from flask_sqlalchemy import SQLAlchemy

from exceptions import KnownException
from exceptions.UserExceptions import LogicGameSizeException, LogicPlayersDontMatchException, ObjectNotFoundException, \
    ObjectAlreadyExistsException, NotTheOwnerOfObjectException
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

    # USER HELPERS
    def is_user_exists(self, username: str) -> bool:
        user_obj = self.models.User.query.filter_by(username=username).first()
        return user_obj is not None

    def get_user(self, username: str):
        user_obj = self.models.User.query.filter_by(username=username).first()
        if user_obj is None:
            raise ObjectNotFoundException("User")
        return user_obj

    # TOKEN HELPERS
    def is_token_exists(self, token: str):
        token_obj = self.models.Token.query.filter_by(id=token).first()
        return token_obj is not None

    def get_token(self, token: str):
        token_obj = self.models.Token.query.filter_by(id=token).first()
        if token_obj is None:
            raise ObjectNotFoundException("Token")
        return token_obj

    # TOURNAMENT_HELPERS
    def is_tournament_exists_id(self, user_id: int, tournament_name: str) -> bool:
        tournament_obj = self.models.Tournament.query.filter_by(user_id=user_id, name=tournament_name).first()
        return tournament_obj is not None

    def is_tournament_owner_id(self, user_id: int, tournament_id: int) -> bool:
        tournament_obj = self.models.Tournament.query.filter_by(id=tournament_id).first()
        return tournament_obj is not None and tournament_obj.user_id == user_id

    def get_tournament_id(self, user_id: int, tournament_id: int):
        tournament_obj = self.models.Tournament.query.filter_by(id=tournament_id, user_id=user_id).first()
        if tournament_obj is None:
            raise ObjectNotFoundException("Tournament")
        return tournament_obj

    # ROUND HELPERS
    def is_round_exists_id(self, user_id: int, tournament_id: int, round_name: str) -> bool:
        if not self.is_tournament_owner_id(user_id, tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")
        round_obj = self.models.Round.query.filter_by(name=round_name, tournament_id=tournament_id).first()
        return round_obj is not None

    def is_round_owner_id(self, user_id: int, round_id: int) -> bool:
        round_obj = self.models.Round.query.filter_by(id=round_id).first()
        return round_obj is not None and round_obj.tournament.user_id == user_id

    def get_round_id(self, user_id: int, round_id: int):
        round_obj = self.models.Round.query.filter_by(id=round_id).first()
        if round_obj is None:
            raise ObjectNotFoundException("Round")
        if not self.is_tournament_owner_id(user_id, round_obj.tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")
        return round_obj

    # PLAYER HELPERS
    def is_player_exists_id(self, user_id: int, tournament_id: int, player_name: str) -> bool:  # FIXME: will change
        if not self.is_tournament_owner_id(user_id, tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")

        p = self.models.Player.query.filter(((self.models.Player.tournament_id == tournament_id) & (
                (self.models.Player.name_first == player_name) |
                (self.models.Player.name_second == player_name)))).first()
        return p is not None

    def get_pair_id(self, user_id: int, pair_id: int):
        pair_obj = self.models.Player.query.filter_by(id=pair_id).first()
        if pair_obj is None:
            raise ObjectNotFoundException("Player")
        if not self.is_tournament_owner_id(user_id, pair_obj.tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")
        return pair_obj

    # WORD HELPERS
    def is_word_exists_id(self, user_id: int, tournament_id: int, word_text: str) -> bool:
        if not self.is_tournament_owner_id(user_id, tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")
        word_obj = self.models.Word.query.filter_by(text=word_text).first()
        return word_obj is not None

    def get_word_id(self, user_id: int, word_id: int):
        word_obj = self.models.Word.query.filter_by(id=word_id).first()
        if word_obj is None:
            raise ObjectNotFoundException("Word")
        if not self.is_tournament_owner_id(user_id, word_obj.tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")
        return word_obj

    # SUBROUND HELPERS
    def is_subround_exists_id(self, user_id: int, round_id: int, subround_name: str) -> bool:
        if not self.is_round_owner_id(user_id, round_id):
            raise NotTheOwnerOfObjectException("Round")
        subround_obj = self.models.Subround.query.filter_by(name=subround_name, round_id=round_id).first()
        return subround_obj is not None

    def is_subround_owner_id(self, user_id: int, subround_id: int) -> bool:
        subround_obj = self.models.Subround.query.filter_by(id=subround_id).first()
        return subround_obj is not None and subround_obj.round.tournament.user_id == user_id

    def get_subround_id(self, user_id: int, subround_id: int):
        subround_obj = self.models.Subround.query.filter_by(id=subround_id).first()
        if subround_obj is None:
            raise ObjectNotFoundException("Subround")
        if not self.is_round_owner_id(user_id, subround_obj.round_id):
            raise NotTheOwnerOfObjectException("Round")
        return subround_obj

    # WORD TAKER AND LINKER

    def get_x_random_words_with_difficulty_y_id(self, user_id: int, tournament_id: int, amount: int, difficulty: int):
        if not self.is_tournament_owner_id(user_id, tournament_id):
            raise NotTheOwnerOfObjectException("Tournament")
        words = self.models.Word.query.filter_by(tournament_id=tournament_id, difficulty=difficulty,
                                                 subround_id=None).order_by(
            self.models.Word.random_seed).limit(amount).all()

        if len(words) < amount:
            raise ObjectNotFoundException("Not enough words")
        return words

    def link_words_with_subround(self, subround_obj, words_list):
        subround_obj.words.extend(words_list)
        self.db.session.add(subround_obj)
        self.db.session.commit()

    # GAME HELPERS

    def is_game_exists_id(self, user_id: int, game_id: int) -> bool:
        game_obj = self.models.Game.query.filter_by(id=game_id).first()
        if game_obj is None:
            return False
        if not self.is_subround_owner_id(user_id, game_obj.subround_id):
            raise NotTheOwnerOfObjectException("Subround")
        return True

    def get_game_id(self, user_id: int, game_id: int):
        game_obj = self.models.Game.query.filter_by(id=game_id).first()
        if game_obj is None:
            raise ObjectNotFoundException("Game")
        if not self.is_subround_owner_id(user_id, game_obj.subround_id):
            raise NotTheOwnerOfObjectException("Subround")
        return game_obj

    # RESULTS HELPERS

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
    def insert_user(self, username: str, pass_hash: str) -> None:
        new_user = self.models.User(username=username, password_hash=pass_hash)
        try:
            self.db.session.add(new_user)
            self.db.session.commit()
        except IntegrityError:
            raise ObjectAlreadyExistsException("User")

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
        token_obj = self.models.Token(id=token_id, expires_in=expires_in, owner=user_obj)
        self.db.session.add(token_obj)
        self.db.session.commit()

    @database_response
    def delete_token(self, token: str) -> None:
        if not self.is_token_exists(token):
            return
        token_obj = self.get_token(token)
        self.db.session.delete(token_obj)
        self.db.session.commit()

    @database_response
    def insert_tournament(self, username: str, tournament_name: str) -> int:
        user_obj = self.get_user(username)
        if self.is_tournament_exists_id(user_obj.id, tournament_name):
            raise ObjectAlreadyExistsException("Tournament")
        new_tournament = self.models.Tournament(name=tournament_name, owner=user_obj)
        self.db.session.add(new_tournament)
        self.db.session.commit()
        return new_tournament.id

    @database_response
    def get_tournaments(self, username: str) -> List:
        user_obj = self.get_user(username)
        return [entities.tournament.Tournament(dbu=t).to_base_info_dict() for t in user_obj.tournaments]

    @database_response
    def get_tournament_info(self, username: str, tournament_id: int) -> Dict:
        user_obj = self.get_user(username)
        tournament_obj = self.get_tournament_id(user_obj.id, tournament_id)
        tournament_info: Dict = entities.tournament.Tournament(tournament_obj).to_base_info_dict()
        tournament_info["rounds"] = self.get_rounds(username, tournament_id)
        tournament_info["players"] = self.get_players(username, tournament_id)
        return tournament_info

    @database_response
    def delete_tournament(self, username: str, tournament_id: int) -> None:
        user_obj = self.get_user(username)
        tournament_obj = self.get_tournament_id(user_obj.id, tournament_id)
        self.db.session.delete(tournament_obj)
        self.db.session.commit()

    @database_response
    def insert_round(self, username: str, tournament_id: int, round_name: str) -> int:
        user_obj = self.get_user(username)
        if self.is_round_exists_id(user_obj.id, tournament_id, round_name):
            raise ObjectAlreadyExistsException("Round")

        tournament_obj = self.get_tournament_id(user_obj.id, tournament_id)
        new_round = self.models.Round(name=round_name, tournament=tournament_obj, results=Counter())
        self.db.session.add(new_round)
        self.db.session.commit()
        return new_round.id

    @database_response
    def get_rounds(self, username: str, tournament_id: int) -> List:
        user_obj = self.get_user(username)
        tournament = self.get_tournament_id(user_obj.id, tournament_id)
        return [entities.round.Round(dbu=r).to_base_info_dict() for r in tournament.rounds]

    @database_response
    def get_round_info(self, username: str, round_id: int) -> Dict:
        user_obj = self.get_user(username)
        round_obj = self.get_round_id(user_obj.id, round_id)
        round_info: Dict = entities.round.Round(round_obj).to_base_info_dict()
        round_info["subrounds"] = self.get_subrounds(username, round_id)
        round_info["players"] = self.get_players_in_round(username, round_id)
        return round_info

    @database_response
    def delete_round(self, username: str, round_id: int) -> None:
        user_obj = self.get_user(username)
        round_to_delete = self.get_round_id(user_obj.id, round_id)
        self.db.session.delete(round_to_delete)
        self.db.session.commit()

    @database_response
    def insert_player(self, username: str, tournament_id: int, name_first: str, name_second: str) -> int:
        user_obj = self.get_user(username)
        if (self.is_player_exists_id(user_obj.id, tournament_id, name_first) or
                self.is_player_exists_id(user_obj.id, tournament_id, name_second)):
            raise ObjectAlreadyExistsException("Player")

        tournament_obj = self.get_tournament_id(user_obj.id, tournament_id)
        new_player = self.models.Player(name_first=name_first, name_second=name_second, tournament=tournament_obj)
        self.db.session.add(new_player)
        self.db.session.commit()
        return new_player.id

    @database_response
    def get_players(self, username: str, tournament_id: int) -> List:
        user_obj = self.get_user(username)
        tournament = self.get_tournament_id(user_obj.id, tournament_id)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in tournament.players]

    @database_response
    def delete_player(self, username: str, pair_id: int) -> None:
        user_obj = self.get_user(username)
        pair_to_delete = self.get_pair_id(user_obj.id, pair_id)
        self.db.session.delete(pair_to_delete)
        self.db.session.commit()

    @database_response
    def insert_word(self, username: str, tournament_id: int, word_text: str, word_difficulty: int) -> int:
        user_obj = self.get_user(username)
        if self.is_word_exists_id(user_obj.id, tournament_id, word_text):
            raise ObjectAlreadyExistsException("Word")

        tournament_obj = self.get_tournament_id(user_obj.id, tournament_id)
        new_word = self.models.Word(text=word_text, difficulty=word_difficulty, tournament=tournament_obj,
                                    random_seed=gen_rand_key())
        self.db.session.add(new_word)
        self.db.session.commit()
        return new_word.id

    @database_response
    def get_words(self, username: str, tournament_id: int) -> List:
        user_obj = self.get_user(username)
        tournament_obj = self.get_tournament_id(user_obj.id, tournament_id)
        return [entities.word.Word(dbu=w).to_base_info_dict() for w in tournament_obj.words]

    @database_response
    def delete_word(self, username: str, word_id: int) -> None:
        user_obj = self.get_user(username)
        word_to_delete = self.get_word_id(user_obj.id, word_id)
        self.db.session.delete(word_to_delete)
        self.db.session.commit()

    @database_response
    def add_pair_id_to_round(self, username: str, round_id: int, pair_id: int) -> None:
        user_obj = self.get_user(username)
        round_obj = self.get_round_id(user_obj.id, round_id)
        player_obj = self.get_pair_id(user_obj.id, pair_id)
        try:  # FIXME: Find some better way to check
            round_obj.players.append(player_obj)
            results = Counter(round_obj.results)
            results[pair_id] = 0
            round_obj.results = results
            self.db.session.add(round_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise ObjectAlreadyExistsException("Player in round")

    @database_response
    def get_players_in_round(self, username: str, round_id: int) -> List:
        user_obj = self.get_user(username)
        round_obj = self.get_round_id(user_obj.id, round_id)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in
                self.db.session.query(self.models.Round).filter_by(id=round_obj.id).first().players]

    @database_response
    def delete_player_from_round(self, username: str, round_id: int, pair_id: int) -> None:
        user_obj = self.get_user(username)
        round_obj = self.get_round_id(user_obj.id, round_id)
        player_obj = self.get_pair_id(user_obj.id, pair_id)
        try:  # FIXME: Duplicated code
            round_obj.players.remove(player_obj)
            results = Counter(round_obj.results)
            del results[pair_id]
            round_obj.results = results
            self.db.session.add(round_obj)
            self.db.session.commit()
        except StaleDataError as e:
            raise ObjectNotFoundException("Player in round")

    @database_response
    def insert_subround(self, username: str, round_id: int, subround_name: str) -> int:
        user_obj = self.get_user(username)
        if self.is_subround_exists_id(user_obj.id, round_id, subround_name):
            raise ObjectAlreadyExistsException("Subround")

        round_obj = self.get_round_id(user_obj.id, round_id)
        new_subround = self.models.Subround(name=subround_name, round=round_obj, results=Counter())
        self.db.session.add(new_subround)
        self.db.session.commit()
        return new_subround.id

    @database_response
    def get_subrounds(self, username: str, round_id: int) -> List:
        user_obj = self.get_user(username)
        round_obj = self.get_round_id(user_obj.id, round_id)
        return [SubroundE(dbu=p).to_base_info_dict() for p in round_obj.subrounds]

    @database_response
    def delete_subround(self, username: str, subround_id: int) -> None:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        self.db.session.delete(subround_obj)
        self.db.session.commit()

    @database_response
    def add_pair_id_to_subround(self, username: str, subround_id: int, pair_id: int) -> None:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        player_obj = self.get_pair_id(user_obj.id, pair_id)
        try:  # FIXME: Find some better way to check
            subround_obj.players.append(player_obj)
            results = Counter(subround_obj.results)
            results[pair_id] = 0
            subround_obj.results = results
            self.db.session.add(subround_obj)
            self.db.session.commit()
        except IntegrityError as e:
            raise ObjectAlreadyExistsException("Player in subround")

    @database_response
    def get_players_in_subround(self, username: str, subround_id: int) -> List:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in
                self.db.session.query(self.models.Subround).filter_by(id=subround_obj.id).first().players]

    @database_response
    def delete_player_from_subround(self, username: str, subround_id: int, pair_id: int) -> None:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        player_obj = self.get_pair_id(user_obj.id, pair_id)
        try:  # FIXME: Duplicated code
            subround_obj.players.remove(player_obj)
            results = Counter(subround_obj.results)
            del results[pair_id]
            subround_obj.results = results
            self.db.session.add(subround_obj)
            self.db.session.commit()
        except StaleDataError as e:
            raise ObjectNotFoundException("Player in round")

    @database_response
    def add_x_words_of_diff_y_to_subround(self, username: str, subround_id: int, words_difficulty: int,
                                          words_amount: int) -> None:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        words = self.get_x_random_words_with_difficulty_y_id(user_obj.id, subround_obj.round.tournament_id,
                                                             words_amount, words_difficulty)
        self.link_words_with_subround(subround_obj, words)

    @database_response
    def get_subround_words(self, username: str, subround_id: int) -> List:
        user_obj = self.get_user(username)
        s = self.get_subround_id(user_obj.id, subround_id)
        return [entities.word.Word(dbu=w).to_base_info_dict() for w in s.words]

    @database_response
    def split_subround_into_games(self, username: str, subround_id: int, games_amount: int) -> List[int]:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        if subround_obj.games.count() > 0:
            raise ObjectAlreadyExistsException("Subround already split")
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
    def get_games(self, username: str, subround_id: int) -> List[int]:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        games_ids = [game.id for game in subround_obj.games]
        return games_ids

    @database_response
    def undo_split_subround_into_games(self, username: str, subround_id: int) -> None:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        if subround_obj.games.count() == 0:
            raise ObjectNotFoundException("Subround not split")
        for game in subround_obj.games:
            self.db.session.delete(game)  # I believe in cascade delete
        self.db.session.commit()

    @database_response
    def get_game_players(self, username: str, game_id: int) -> List:
        user_obj = self.get_user(username)
        game_obj = self.get_game_id(user_obj.id, game_id)
        return [entities.player.Player(dbu=p).to_base_info_dict() for p in game_obj.players]

    @database_response
    def set_game_result(self, username: str, game_id: int, result: Counter) -> None:
        user_obj = self.get_user(username)
        game_obj = self.get_game_id(user_obj.id, game_id)
        if game_obj.results_set:
            raise ObjectAlreadyExistsException("Game results")
        if result.keys() != set([p.id for p in game_obj.players]):
            raise LogicPlayersDontMatchException()
        game_obj.results_set = True
        game_obj.results = result
        self.db.session.add(game_obj)
        self.db.session.commit()
        self.update_add_results_push_from_game(game_obj)

    @database_response
    def get_game_result(self, username: str, game_id: int) -> Counter:
        user_obj = self.get_user(username)
        game_obj = self.get_game_id(user_obj.id, game_id)
        if not game_obj.results_set:
            raise ObjectNotFoundException("Game results")
        return game_obj.results

    @database_response
    def delete_game_result(self, username: str, game_id: int) -> None:
        user_obj = self.get_user(username)
        game_obj = self.get_game_id(user_obj.id, game_id)
        if not game_obj.results_set:
            raise ObjectNotFoundException("Game results")
        self.update_subtract_results_push_from_game(game_obj)
        game_obj.results_set = False
        self.db.session.add(game_obj)
        self.db.session.commit()

    @database_response
    def get_subround_result(self, username: str, subround_id: int) -> Counter:
        user_obj = self.get_user(username)
        subround_obj = self.get_subround_id(user_obj.id, subround_id)
        if subround_obj.results is None:
            raise ObjectNotFoundException("Game results")
        return subround_obj.results

    @database_response
    def get_round_result(self, username: str, round_id: int) -> Counter:
        user_obj = self.get_user(username)
        round_obj = self.get_round_id(user_obj.id, round_id)
        if round_obj.results is None:
            raise ObjectNotFoundException("Game results")
        return round_obj.results

    @database_response
    def clear_all_tables(self):
        self.db.drop_all()
        self.db.create_all()

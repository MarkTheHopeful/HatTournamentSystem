"""
Query functions are implemented in this file
Used by the file routes.py
Before decorator functions return tuple "code, data" [Tuple[int, Dictionary]]
Decorator handles exceptions and returns the flask Response object
"""

import datetime
from app.extensions import dbm
from exceptions.UserExceptions import ObjectNotFoundException
from utils.encrypt import encrypt_password, check_password
from config import Config
from exceptions import KnownException
from app.db_manager import DBException
from utils.utils import gen_token, full_stack
from utils import template_data  # FIXME: DEBUG only
from flask import make_response
from flask import Response
from typing import Callable, Tuple, Dict, Counter


def function_response(result_function: Callable[..., Tuple[int, Dict]]) -> Callable[..., Response]:
    """
    :param result_function: function to wrap, returns code (Int) and data (JSON)
    :return: wrapped function, input stays same, exceptions handled, output converted to str(Response)
    Wrapper for all functions in routes
    Gets code and data from the wrapped function and returns a [[app.functions.Response]] object, casted to string
    If an exception occurs, its string goes to the data["Error"] and logs (to stdout)
    Catches DBExceptions with error codes 6xx (699 for unknown db error)
    Catches all other exceptions with error code 500
    """

    def wrapped(*args, **kwargs) -> Response:
        try:
            status_code, data = result_function(*args, **kwargs)
        except DBException as e:
            status_code = 500
            data = {"Error": str(e), "Stack": full_stack()}
        except KnownException as e:
            status_code = e.code
            data = {"Message": e.message}
        except Exception as e:
            status_code = 500
            data = {"Error": str(e), "Stack": full_stack()}
        response = make_response(data, status_code)
        response.headers['Content-Type'] = 'application/json'
        return response

    return wrapped


def token_auth(token: str) -> str:
    """
    :param token: user token
    :return: username, if token is valid, otherwise throws ObjectNotFound("Token")
    """
    username, exp_time = dbm.get_username_and_exptime_by_token(token)

    if exp_time < datetime.datetime.utcnow():
        dbm.delete_token(token)
        raise ObjectNotFoundException("Token")  # TODO: seems not good, I guess
    return username


@function_response
def status() -> Tuple[int, Dict]:  # TODO: rewrite to add meaningful information
    """
    Get the server's state
    :return: 200, {'State': 'Active', 'API version': [str], 'DB manager': 'OK/FAILED'}
    """
    code = 200
    data = {'State': 'Active', 'API version': 'v1', 'DB manager': 'OK' if dbm.is_ok() else "FAILED"}
    return code, data


@function_response
def login(username: str, password: str) -> Tuple[int, Dict]:
    """
    :param username: not empty, should be real username
    :param password: not empty, should be user's password
    :return: 201, {'Token': <token>} on success, errors otherwise
    Throws exceptions, but they are handled in wrapper
    """

    user_password_hash: str = dbm.get_password_hash(username)

    if not check_password(password, user_password_hash):
        raise ObjectNotFoundException("User")

    tok_uuid, tok_exp = gen_token()
    dbm.insert_token(tok_uuid, tok_exp, username)
    code = 201
    data = {'Token': tok_uuid}

    return code, data


@function_response
def register(username: str, password: str) -> Tuple[int, Dict]:
    """
    :param username: new username, should be unique and consist only of allowed characters
    :param password: password, should be strong
    :return: 201, {} if success; 400, {} if username is already in use
    Throws exceptions, but they are handled in wrapper
    TODO: add password check
    TODO: add allowed characters list and verification
    """
    pass_hash = encrypt_password(password)
    dbm.insert_user(username, pass_hash)

    return 201, {}


@function_response
def new_tournament(token: str, name: str) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param name: name of new tournament to create
    :return: 201, {"ID": tournament_id} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    tournament_id = dbm.insert_tournament(username, name)

    return 201, {"ID": tournament_id}


@function_response
def get_tournaments(token: str) -> Tuple[int, Dict]:
    """
    :param token: session token
    :return: 200, {"Tournaments": list of tournaments} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    tournaments = dbm.get_tournaments(username)

    return 200, {"Tournaments": tournaments}


@function_response
def new_player(token: str, tournament_id: int, name_first: str, name_second: str) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param tournament_id: id of the tournament to which the players will be added
    :param name_first: name of the first player in pair
    :param name_second: name of the second player in pair
    :return: 201, {"ID": player_id} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_player(username, tournament_id, name_first, name_second)

    return 201, {"ID": new_id}


@function_response
def get_players(token: str, tournament_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param tournament_id: id of the tournament
    :return: 200, {"Players": list of players} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    players = dbm.get_players(username, tournament_id)

    return 200, {"Players": players}


@function_response
def delete_player(token: str, pair_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param pair_id: id of the pair to delete
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_player(username, pair_id)

    return 200, {}


@function_response
def new_word(token: str, tournament_id: int, word_text: str, word_difficulty: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param tournament_id: id of the tournament to which the word will be added
    :param word_text: text of word
    :param word_difficulty: how difficult is it to explain the word
    :return: 201, {"ID": word_id} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_word(username, tournament_id, word_text, word_difficulty)

    return 201, {"ID": new_id}


@function_response
def get_words(token: str, tournament_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param tournament_id: id of the tournament
    :return: 200, {"Words": list of words} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    words = dbm.get_words(username, tournament_id)

    return 200, {"Words": words}


@function_response
def delete_word(token: str, word_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param word_id: id of the word to delete
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_word(username, word_id)

    return 200, {}


@function_response
def new_round(token: str, tournament_id: int, round_name: str) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param tournament_id: id of the tournament to add round
    :param round_name: name of the round
    :return: 200, {"ID": round id} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_round(username, tournament_id, round_name)

    return 200, {"ID": new_id}


@function_response
def get_rounds(token: str, tournament_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param tournament_id: id of the tournament
    :return: 200, {"Rounds": list of rounds} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    rounds = dbm.get_rounds(username, tournament_id)

    return 200, {"Rounds": rounds}


@function_response
def delete_round(token: str, round_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param round_id: id of the round to delete
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_round(username, round_id)

    return 200, {}


@function_response
def add_player_to_round(token: str, round_id: int, pair_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param round_id: id of the round to interact with
    :param pair_id: id of the pair (player) to add into round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.add_pair_id_to_round(username, round_id, pair_id)

    return 200, {}


@function_response
def get_players_in_round(token: str, round_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param round_id: id of the round from which take players
    :return: 200, {"Players": list of players in round} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    players = dbm.get_players_in_round(username, round_id)

    return 200, {"Players": players}


@function_response
def delete_player_from_round(token: str, round_id: int, pair_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param round_id: id of the round to interact with
    :param pair_id: id of the pair (player) to delete from round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.delete_player_from_round(username, round_id, pair_id)
    return 200, {}


@function_response
def new_subround(token: str, round_id: int, subround_name: str) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param round_id: id of the round to interact with
    :param subround_name: name of new subround
    :return: 201, {"ID": <id>} on success, errors on error.
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    new_id = dbm.insert_subround(username, round_id, subround_name)
    return 201, {"ID": new_id}


@function_response
def get_subrounds(token: str, round_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param round_id: id of the round to interact with
    :return: 200, {"Subrounds": list of subrounds} on success, errors on error.
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    return 200, {"Subrounds": dbm.get_subrounds(username, round_id)}


@function_response
def delete_subround(token: str, subround_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to delete
    :return: 200, {} on success, errors on error.
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_subround(username, subround_id)

    return 200, {}


@function_response
def add_player_to_subround(token: str, subround_id: int, pair_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :param pair_id: id of the pair (player) to add into round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.add_pair_id_to_subround(username, subround_id, pair_id)

    return 200, {}


@function_response
def get_players_in_subround(token: str, subround_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround from which take players
    :return: 200, {"Players": list of players in round} on success,
    """
    username = token_auth(token)
    players = dbm.get_players_in_subround(username, subround_id)

    return 200, {"Players": players}


@function_response
def delete_player_from_subround(token: str, subround_id: int, pair_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :param pair_id: id of the pair (player) to delete from round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.delete_player_from_subround(username, subround_id, pair_id)
    return 200, {}


@function_response
def add_x_words_of_diff_y_to_subround(token: str, subround_id: int,
                                      words_difficulty: int, words_amount: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :param words_difficulty: difficulty of words to add
    :param words_amount: amount of words to add
    :return: 200, {} if added, errors if error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.add_x_words_of_diff_y_to_subround(username, subround_id, words_difficulty, words_amount)
    return 200, {}


@function_response
def get_subround_words(token: str, subround_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :return: 200, {"Words": list of words in subround} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    words = dbm.get_subround_words(username, subround_id)

    return 200, {"Words": words}


@function_response
def split_subround_into_games(token: str, subround_id: int, games_amount: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :param games_amount: amount of games to split round into
    :return: 200, {"Games": list of IDs of games} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    games_ids = dbm.split_subround_into_games(username, subround_id, games_amount)

    return 200, {"Games": games_ids}


@function_response
def get_games(token: str, subround_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :return: 200, {"Games": list of IDs of games} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    games_ids = dbm.get_games(username, subround_id)

    return 200, {"Games": games_ids}


@function_response
def undo_split_subround_into_games(token: str, subround_id: int) -> Tuple[int, Dict]:
    """
    :param token: session token
    :param subround_id: id of the subround to interact with
    :return: 200, {} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.undo_split_subround_into_games(username, subround_id)

    return 200, {}


@function_response
def get_game_players(token: str, game_id: int) -> Tuple[int, Dict]:
    """
       :param token: session token
       :param game_id: id of game which information to get
       :return: 200, {"Players": List of players} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    players = dbm.get_game_players(username, game_id)

    return 200, {"Players": players}


@function_response
def set_game_result(token: str, game_id: int, result: Counter) -> Tuple[int, Dict]:
    """
       :param token: session token
       :param game_id: id of game which information to set
       :param result: result of game
       :return: 201, {} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    dbm.set_game_result(username, game_id, result)

    return 201, {}


@function_response
def get_game_result(token: str, game_id: int) -> Tuple[int, Dict]:
    """
       :param token: session token
       :param game_id: id of game which information to get
       :return: 200, {"Result": Dict[Player_id : result]} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    game_result = dbm.get_game_result(username, game_id)

    return 200, {"Result": game_result.most_common()}


@function_response
def delete_game_result(token: str, game_id: int) -> Tuple[int, Dict]:
    """
       :param token: session token
       :param game_id: id of game which information to get
       :return: 200, {} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    dbm.delete_game_result(username, game_id)

    return 200, {}


@function_response
def get_subround_result(token: str, subround_id: int) -> Tuple[int, Dict]:
    """
       :param token: session token
       :param subround_id: id of subround which information to get
       :return: 200, {"Result": Dict[Player_id : result]} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    subround_result = dbm.get_subround_result(username, subround_id)

    return 200, {"Result": subround_result.most_common()}


@function_response
def get_round_result(token: str, round_id: int) -> Tuple[int, Dict]:
    """
       :param token: session token
       :param round_id: id of round which information to get
       :return: 200, {"Result": Dict[Player_id, result]} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    round_result = dbm.get_round_result(username, round_id)

    return 200, {"Result": round_result.most_common()}


@function_response
def drop_tables(secret_code):
    """
    :param secret_code: admin secret from config
    :return: 404, {} if the secret code is incorrect
    200, {} if everything is dropped and recreated successfully
    """
    if secret_code != Config.ADMIN_SECRET:
        return 404, {}
    dbm.clear_all_tables()
    return 200, {}


# FIXME: outdated, probably
@function_response
def fill_with_example(secret_code):
    """
    :param secret_code: admin secret from config
    :return: 404, {} if the secret code is incorrect
    200, {} if example fill executed successfully
    May throw other exceptions
    """
    if secret_code != Config.ADMIN_SECRET:
        return 404, {}

    example_username = template_data.EXAMPLE_USER[0]
    dbm.insert_user(example_username, encrypt_password(template_data.EXAMPLE_USER[1]))

    example_tournament = template_data.EXAMPLE_TOURNAMENT_NAME
    tournament_id = dbm.insert_tournament(example_username, example_tournament)
    round_ids = []

    for round_name in template_data.EXAMPLE_ROUNDS_NAMES:
        round_ids.append(dbm.insert_round(example_username, tournament_id, round_name))

    subround_ids = []
    for subround_name, round_ind in template_data.EXAMPLE_SUBROUNDS:
        subround_ids.append(dbm.insert_subround(example_username, round_ids[round_ind], subround_name))

    for word, diff in template_data.EXAMPLE_WORDS:
        dbm.insert_word(example_username, tournament_id, word, diff)

    for p1, p2, ri, sri, ind in template_data.EXAMPLE_PLAYERS:
        dbm.insert_player(example_username, tournament_id, p1, p2)
        dbm.add_pair_id_to_round(example_username, round_ids[ri], ind)
        dbm.add_pair_id_to_subround(example_username, subround_ids[sri], ind)

    return 200, {}

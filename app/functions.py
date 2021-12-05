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
from typing import Callable, Tuple, Dict


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
def get_rounds(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament
    :return: 200, {"Rounds": <list of rounds>} on success; 403, {} if not the owner
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    rounds = dbm.get_rounds(username, tournament_name)

    return 200, {"Rounds": rounds}


@function_response
def delete_round(token, tournament_name, round_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament from which the round will be deleted
    :param round_name: name of the round to delete
    :return: 200, {} on success; 400, {} if no such round in tournament, 403, {} if not owner of tournament
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_round(username, tournament_name, round_name)

    return 200, {}


@function_response
def add_player_to_round(token, tournament_name, round_name, pair_id):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param pair_id: id of the pair (player) to add into round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.add_pair_id_to_round(username, tournament_name, round_name, pair_id)

    return 200, {}


@function_response
def get_players_in_round(token, tournament_name, round_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round from which take players
    :return: 200, {"Players":<list of players in round>} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    players = dbm.get_players_in_round(username, tournament_name, round_name)

    return 200, {"Players": players}


@function_response
def delete_player_from_round(token, tournament_name, round_name, pair_id):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param pair_id: id of the pair (player) to delete from round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.delete_player_from_round(username, tournament_name, round_name, pair_id)
    return 200, {}


@function_response
def new_subround(token, tournament_name, round_name, subround_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param subround_name: name of new subround
    :return: 200, {"Id": <id>} on success, errors on error.
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    new_id = dbm.insert_subround(username, tournament_name, round_name, subround_name)
    return 200, {"Id": new_id}


@function_response
def get_subrounds(token, tournament_name, round_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :return: 200, {"Subrounds": <list of subrounds>} on success, errors on error.
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    return 200, {"Subrounds": dbm.get_subrounds(username, tournament_name, round_name)}


@function_response
def delete_subround(token, tournament_name, round_name, subround_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param subround_name: name of the subround to delete
    :return: 200, {} on success, errors on error.
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_subround(username, tournament_name, round_name, subround_name)

    return 200, {}


@function_response
def add_player_to_subround(token, tournament_name, round_name, subround_name, pair_id):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param subround_name: name of the subround to interact with
    :param pair_id: id of the pair (player) to add into round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.add_pair_id_to_subround(username, tournament_name, round_name, subround_name, pair_id)

    return 200, {}


@function_response
def get_players_in_subround(token, tournament_name, round_name, subround_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round from which take players
    :param subround_name: name of the subround from which take players
    :return: 200, {"Players":<list of players in round>} on success,
    """
    username = token_auth(token)
    players = dbm.get_players_in_subround(username, tournament_name, round_name, subround_name)

    return 200, {"Players": players}


@function_response
def delete_player_from_subround(token, tournament_name, round_name, subround_name, pair_id):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param subround_name: name of the subround to interact with
    :param pair_id: id of the pair (player) to delete from round
    :return: 200, {} on success; errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.delete_player_from_subround(username, tournament_name, round_name, subround_name, pair_id)
    return 200, {}


@function_response
def add_x_words_of_diff_y_to_subround(token, tournament_name, round_name, subround_name,
                                      words_difficulty, words_amount):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name is someone reading this? interact with
    :param subround_name: name of the subround to interact with
    :param words_difficulty: difficulty of words to add
    :param words_amount: amount of words to add
    :return: 200, {} if added, errors if error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.add_x_words_of_diff_y_to_subround(username, tournament_name, round_name, subround_name, words_difficulty,
                                          words_amount)
    return 200, {}


@function_response
def get_subround_words(token, tournament_name, round_name, subround_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name is someone reading this? interact with
    :param subround_name: name of the subround to interact with
    :return: 200, {"Words": <list of words in subround>} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    words = dbm.get_subround_words(username, tournament_name, round_name, subround_name)

    return 200, {"Words": words}


@function_response
def split_subround_into_games(token, tournament_name, round_name, subround_name, games_amount):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name is someone reading this? interact with
    :param subround_name: name of the subround to interact with
    :param games_amount: amount of games to split round into
    :return: 200, {"Ids": <list of IDs of games>} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    games_ids = dbm.split_subround_into_games(username, tournament_name, round_name, subround_name, games_amount)

    return 200, {"Ids": games_ids}


@function_response
def get_games(token, tournament_name, round_name, subround_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name is someone reading this? interact with
    :param subround_name: name of the subround to interact with
    :return: 200, {"Games": <list of IDs of games>} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    games_ids = dbm.get_games(username, tournament_name, round_name, subround_name)

    return 200, {"Ids": games_ids}


@function_response
def undo_split_subround_into_games(token, tournament_name, round_name, subround_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name is someone reading this? interact with
    :param subround_name: name of the subround to interact with
    :return: 200, {} on success, errors on error
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)

    dbm.undo_split_subround_into_games(username, tournament_name, round_name, subround_name)

    return 200, {}


@function_response
def get_game_players(token, tournament_name, game_id):
    """
       :param token: session token
       :param tournament_name: name of the tournament to interact with
       :param game_id: id of game which information to get
       :return: 200, {"Players": <list_of_players>} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    players = dbm.get_game_players(username, tournament_name, game_id)

    return 200, {"Players": players}


@function_response
def set_game_result(token, tournament_name, game_id, result):
    """
       :param token: session token
       :param tournament_name: name of the tournament to interact with
       :param game_id: id of game which information to set
       :param result: result of game
       :return: 200, {} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    dbm.set_game_result(username, tournament_name, game_id, result)

    return 200, {}


@function_response
def get_game_result(token, tournament_name, game_id):
    """
       :param token: session token
       :param tournament_name: name of the tournament to interact with
       :param game_id: id of game which information to get
       :return: 200, {"Result": <dict Player_id : result>} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    game_result = dbm.get_game_result(username, tournament_name, game_id)

    return 200, {"Result": game_result.most_common()}


@function_response
def delete_game_result(token, tournament_name, game_id):
    """
       :param token: session token
       :param tournament_name: name of the tournament to interact with
       :param game_id: id of game which information to get
       :return: 200, {} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    dbm.delete_game_result(username, tournament_name, game_id)

    return 200, {}


@function_response
def get_subround_result(token, tournament_name, round_name, subround_name):
    """
       :param token: session token
       :param tournament_name: name of the tournament to interact with
       :param round_name: name of round which information to get
       :param subround_name: name of subround which information to get
       :return: 200, {"Result": <dict Player_id : result>} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    subround_result = dbm.get_subround_result(username, tournament_name, round_name, subround_name)

    return 200, {"Result": subround_result.most_common()}


@function_response
def get_round_result(token, tournament_name, round_name):
    """
       :param token: session token
       :param tournament_name: name of the tournament to interact with
       :param round_name: name of round which information to get
       :return: 200, {"Result": <dict Player_id : result>} on success, errors on error
       Throws exceptions, but they are handled in wrapper
       """
    username = token_auth(token)

    round_result = dbm.get_round_result(username, tournament_name, round_name)

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
    dbm.insert_tournament(example_username, example_tournament)

    for round_name in template_data.EXAMPLE_ROUNDS_NAMES:
        dbm.insert_round(example_username, example_tournament, round_name)

    for subround_name, round_ind in template_data.EXAMPLE_SUBROUNDS:
        dbm.insert_subround(example_username, example_tournament, template_data.EXAMPLE_ROUNDS_NAMES[round_ind],
                            subround_name)

    for word, diff in template_data.EXAMPLE_WORDS:
        dbm.insert_word(example_username, 0, word, diff)    # ???

    for p1, p2, ri, sri, ind in template_data.EXAMPLE_PLAYERS:
        dbm.insert_player(example_username, example_tournament, p1, p2)
        dbm.add_pair_id_to_round(example_username, example_tournament, template_data.EXAMPLE_ROUNDS_NAMES[ri], ind)
        dbm.add_pair_id_to_subround(example_username, example_tournament, template_data.EXAMPLE_ROUNDS_NAMES[ri],
                                    template_data.EXAMPLE_SUBROUNDS[sri][0], ind)

    return 200, {}

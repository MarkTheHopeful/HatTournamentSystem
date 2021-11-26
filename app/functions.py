# There the functions are being implemented.
# Then the routes.py will use them
# The functions always produce output as JSON
# The format is: {code: CODE, state: STATE, data: {JSON}}, where code is the status code
# State is the description of the code
# And the data is the product, which the function returns
# FIXME: the file is too bloated! Should add more decorators to remove repetition


import json
import datetime
from app.extensions import dbm
from utils.encrypt import encrypt_password, check_password
from config import Config
from exceptions.DBExceptions import DBException, DBObjectNotFound, DBObjectAlreadyExists
from utils.utils import gen_token, full_stack
from entities.user import User
from entities.tournament import Tournament


class Response:  # FIXME: Exists an actual Flask.Response object!
    code = 500
    data = None

    def __init__(self, code=500, data=None):
        self.code = code
        if data is None:
            data = json.dumps({})
        self.data = json.loads(data)

    def __str__(self):
        return str(json.dumps({"data": self.data}))


def function_response(result_function):
    """
    :param result_function: function to wrap, have to return code (Int) and data (JSON)
    :return: wrapped function, input stays same, exceptions handled, output converted to str(Response)
    Wrapper for all functions in routes
    Gets code and data from the wrapped function and returns a [[app.functions.Response]] object, casted to string
    If an exception occurs, its string goes to the data["Error"] and logs (to stdout)
    Catches DBExceptions with error codes 6xx (699 for unknown db error)
    Catches all other exceptions with error code 500
    """

    def wrapped(*args, **kwargs):
        code = 500
        try:
            code, data = result_function(*args, **kwargs)
        except DBException as e:
            code = e.code
            data = json.dumps({"error": str(e), "stack": full_stack()})
            print("DBException:", e)
        # except GameException as e:
        #     code = 410
        #     data = json.dumps({"Error": str(e), "Stack": full_stack()})
        #     print("GameException:", e)
        except Exception as e:
            data = json.dumps({"error": str(e), "stack": full_stack()})
            print(e)
        return str(Response(code, data)), code

    return wrapped


def token_auth(token):
    """
    :param token: user token, string
    :return: -1, if no such token exists or if the token is outdated, username otherwise
    """
    try:
        username, exp_time = dbm.get_username_and_exptime_by_token(token)
    except DBObjectNotFound:
        return -1
    if exp_time < datetime.datetime.utcnow():
        dbm.delete_token(token)
        return -1
    return username


@function_response
def status():  # TODO: rewrite to add meaningful information
    """
    Get the server's state
    :return: 200, 'State' : 'Ok/Failed', 'API version', 'DB manager' : 'Ok/FAILED', 'Game manager': 'Ok/FAILED',
     'Amount of games', 'Length of queue';
    """
    code = 200
    result = {'State': 'Active', 'API version': 'v1', 'DB manager': 'Ok' if dbm.is_ok() else "FAILED"}
    data = json.dumps(result)
    return code, data


@function_response
def login(username, password):
    """
    :param username: not empty, should be real username
    :param password: not empty, should be user's password
    :return: 404, {} if there is no user with such credentials; 200, {'Token': <token>} if there is
    Can throw DBException, but shouldn't
    """
    try:
        u_hash = dbm.get_passhash_by_username(username)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data

    if not check_password(password, u_hash):
        code = 404
        data = json.dumps({"Message": "User not found"})
        return code, data

    tok_uuid, tok_exp = gen_token()
    dbm.insert_token_to_username(tok_uuid, tok_exp, username)
    code = 200
    data = json.dumps({'Token': tok_uuid})
    return code, data


@function_response
def register(username, password):
    """
    :param username: new username, should be unique and consist only of allowed characters
    :param password: password, should be strong
    :return: 200, {} if success; 400, {} if username is already in use
    Can throw DBException, but shouldn't
    TODO: add password check
    TODO: add allowed characters list and verification
    """
    pass_hash = encrypt_password(password)
    try:
        dbm.insert_user(User(username=username), pass_hash)
    except DBObjectAlreadyExists as e:
        code = 400
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def new_tournament(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of new tournament to create
    :return: 200, {} if success; 403, {} if token is invalid
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.insert_tournament(Tournament(name=tournament_name), username)
    except DBObjectAlreadyExists as e:
        code = 400
        data = json.dumps({"Message": e.message})
        return code, data
    return 200, json.dumps({})


@function_response
def get_tournaments(token):
    """
    :param token: session token
    :return: 200, {"tournaments": <list of tournaments>} if success; 403, {} if token is invalid
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    tournaments = dbm.get_tournaments(username)
    return 200, json.dumps({"Tournaments": tournaments})


@function_response
def new_player(token, tournament_name, name_first, name_second):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :param name_first: name of the first player in pair
    :param name_second: name of the second player in pair
    :return: 200, {} on success; 400, {} if one of players is already in tournament, 403, {} is not owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.insert_player(username, tournament_name, name_first, name_second)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    except DBObjectAlreadyExists as e:
        code = 400
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def get_players(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :return: 200, {"Players": <list of players>} on success; 403, {} if not the owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        players = dbm.get_players(username, tournament_name)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    return 200, json.dumps({"Players": players})


@function_response
def delete_player(token, tournament_name, name_first, name_second):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :param name_first: name of the first player in pair
    :param name_second: name of the second player in pair
    :return: 200, {} on success; 400, {} if no such pair in tournament, 403, {} is not owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.delete_player(username, tournament_name, name_first, name_second)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def new_word(token, tournament_name, word_text, word_difficulty):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the word will be added
    :param word_text: text of word
    :param word_difficulty: how difficult is it to explain the word
    :return: 200, {} on success; 400, {} if the word is already in tournament, 403, {} is not owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.insert_word(username, tournament_name, word_text, word_difficulty)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    except DBObjectAlreadyExists as e:
        code = 400
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def get_words(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament
    :return: 200, {"Words": <list of words>} on success; 403, {} if not the owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        words = dbm.get_words(username, tournament_name)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    return 200, json.dumps({"Words": words})


@function_response
def delete_word(token, tournament_name, word_text):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :param word_text: word
    :return: 200, {} on success; 400, {} if no such word in tournament, 403, {} if not owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.delete_word(username, tournament_name, word_text)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def new_round(token, tournament_name, round_name, round_difficulty):
    """
    :param token: session token
    :param tournament_name: name of the tournament to add round
    :param round_name: name of the round
    :param round_difficulty: expected difficulty of the round
    :return: 200, {} on success; 400, {} if round with same name is already in tournament; 403, {} if not owner
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.insert_round(username, tournament_name, round_name, round_difficulty)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    except DBObjectAlreadyExists as e:
        code = 400
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def get_rounds(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament
    :return: 200, {"Rounds": <list of rounds>} on success; 403, {} if not the owner
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        rounds = dbm.get_rounds(username, tournament_name)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    return 200, json.dumps({"Rounds": rounds})


@function_response
def delete_round(token, tournament_name, round_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament from which the round will be deleted
    :param round_name: name of the round to delete
    :return: 200, {} on success; 400, {} if no such round in tournament, 403, {} if not owner of tournament
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.delete_round(username, tournament_name, round_name)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def add_player_to_round(token, tournament_name, round_name, pair_id):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param pair_id: id of the pair (player) to add into round
    :return: 200, {} on success; 400, {} if the pair is already in the round;
    404, {} if no such pair or round; 403, {} if not owner
    """

    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.add_pair_id_to_round(username, tournament_name, round_name, pair_id)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    except DBObjectAlreadyExists as e:
        code = 400
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def get_players_in_round(token, tournament_name, round_name):
    """
        :param token: session token
        :param tournament_name: name of the tournament to interact with
        :param round_name: name of the round from which take players
        :return: 200, {"Players":<list of players in round>} on success;
        404, {} if no such round; 403, {} if not owner
        """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        players = dbm.get_players_in_round(username, tournament_name, round_name)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    return 200, json.dumps({"Players": players})


@function_response
def delete_player_from_round(token, tournament_name, round_name, pair_id):
    """
    :param token: session token
    :param tournament_name: name of the tournament to interact with
    :param round_name: name of the round to interact with
    :param pair_id: id of the pair (player) to delete from round
    :return: 200, {} on success; 400, {} if the pair is not in the round;
    404, {} if no such pair or round; 403, {} if not owner
    """

    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({"Message": "Invalid/Outdated token"})
        return code, data
    try:
        dbm.delete_player_from_round(username, tournament_name, round_name, pair_id)
    except DBObjectNotFound as e:
        code = 404
        data = json.dumps({"Message": e.message})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def drop_tables(secret_code):
    """
    :param secret_code: admin secret from config
    :return: 403, {} if the secret code is incorrect
    200, {} if everything is dropped and recreated successfully
    """
    if secret_code != Config.ADMIN_SECRET:
        return 403, json.dumps({})
    dbm.clear_all_tables()
    return 200, json.dumps({})

# There the functions are being implemented.
# Then the routes.py will use them
# The functions always produce output as JSON
# The format is: {code: CODE, state: STATE, data: {JSON}}, where code is the status code    # FIXME: outdated
# State is the description of the code
# And the data is the product, which the function returns
# TODO: update documentation


import json
import datetime
from app.extensions import dbm
from exceptions.LogicExceptions import LogicException
from utils.encrypt import encrypt_password, check_password
from config import Config
from exceptions.DBExceptions import DBException, DBObjectNotFound
from utils.utils import gen_token, full_stack
from entities.user import User
from entities.tournament import Tournament
from utils import template_data  # FIXME: DEBUG only


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


# FIXME: Now this thing handles all the exceptions
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
            if e.code != 699:
                data = json.dumps({"Message": e.message})
            else:
                data = json.dumps({"Error": str(e), "Stack": full_stack()})
                print("DBException:", e)
            e.code = code
        except LogicException as e:
            code = e.code
            data = json.dumps({"Message": e.message})
        except Exception as e:
            data = json.dumps({"Error": str(e), "Stack": full_stack()})
            print(e)
        return str(Response(code, data)), code

    return wrapped


def token_auth(token):
    """
    :param token: user token, string
    :return: username, if token exists and the token is not outdated, otherwise throws DBObjectNotFound("Token")
    """
    username, exp_time = dbm.get_username_and_exptime_by_token(token)

    if exp_time < datetime.datetime.utcnow():
        dbm.delete_token(token)
        raise DBObjectNotFound("Token")  # TODO: seems not good, I guess
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
    Throws exceptions, but they are handled in wrapper
    """

    u_hash = dbm.get_password_hash(username)

    if not check_password(password, u_hash):
        raise DBObjectNotFound("User")

    tok_uuid, tok_exp = gen_token()
    dbm.insert_token(tok_uuid, tok_exp, username)
    code = 200
    data = json.dumps({'Token': tok_uuid})

    return code, data


@function_response
def register(username, password):
    """
    :param username: new username, should be unique and consist only of allowed characters
    :param password: password, should be strong
    :return: 200, {} if success; 400, {} if username is already in use
    Throws exceptions, but they are handled in wrapper
    TODO: add password check
    TODO: add allowed characters list and verification
    """
    pass_hash = encrypt_password(password)
    dbm.insert_user(User(username=username), pass_hash)

    return 200, json.dumps({})


@function_response
def new_tournament(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of new tournament to create
    :return: 200, {} if success; 403, {} if token is invalid
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_tournament(username, Tournament(name=tournament_name))
    return 200, json.dumps({"Id": new_id})


@function_response
def get_tournaments(token):
    """
    :param token: session token
    :return: 200, {"tournaments": <list of tournaments>} if success; 403, {} if token is invalid
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
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
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_player(username, tournament_name, name_first, name_second)

    return 200, json.dumps({"Id": new_id})


@function_response
def get_players(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :return: 200, {"Players": <list of players>} on success; 403, {} if not the owner of tournament
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    players = dbm.get_players(username, tournament_name)

    return 200, json.dumps({"Players": players})


@function_response
def delete_player(token, tournament_name, name_first, name_second):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :param name_first: name of the first player in pair
    :param name_second: name of the second player in pair
    :return: 200, {} on success; 400, {} if no such pair in tournament, 403, {} is not owner of tournament
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_player(username, tournament_name, name_first, name_second)

    return 200, json.dumps({})


@function_response
def new_word(token, tournament_name, word_text, word_difficulty):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the word will be added
    :param word_text: text of word
    :param word_difficulty: how difficult is it to explain the word
    :return: 200, {} on success; 400, {} if the word is already in tournament, 403, {} is not owner of tournament
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_word(username, tournament_name, word_text, word_difficulty)

    return 200, json.dumps({"Id": new_id})


@function_response
def get_words(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament
    :return: 200, {"Words": <list of words>} on success; 403, {} if not the owner of tournament
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    words = dbm.get_words(username, tournament_name)

    return 200, json.dumps({"Words": words})


@function_response
def delete_word(token, tournament_name, word_text):
    """
    :param token: session token
    :param tournament_name: name of the tournament to which the players will be added
    :param word_text: word
    :return: 200, {} on success; 400, {} if no such word in tournament, 403, {} if not owner of tournament
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    dbm.delete_word(username, tournament_name, word_text)

    return 200, json.dumps({})


@function_response
def new_round(token, tournament_name, round_name):
    """
    :param token: session token
    :param tournament_name: name of the tournament to add round
    :param round_name: name of the round
    :return: 200, {} on success; 400, {} if round with same name is already in tournament; 403, {} if not owner
    Throws exceptions, but they are handled in wrapper
    """
    username = token_auth(token)
    new_id = dbm.insert_round(username, tournament_name, round_name)

    return 200, json.dumps({"Id": new_id})


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

    return 200, json.dumps({"Rounds": rounds})


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

    return 200, json.dumps({})


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

    return 200, json.dumps({})


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

    return 200, json.dumps({"Players": players})


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
    return 200, json.dumps({})


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
    return 200, json.dumps({"Id": new_id})


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

    return 200, json.dumps({"Subrounds": dbm.get_subrounds(username, tournament_name, round_name)})


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

    return 200, json.dumps({})


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

    return 200, json.dumps({})


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

    return 200, json.dumps({"Players": players})


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
    return 200, json.dumps({})


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
    return 200, json.dumps({})


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

    return 200, json.dumps({"Words": words})


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

    return 200, json.dumps({"Ids": games_ids})


@function_response
def drop_tables(secret_code):
    """
    :param secret_code: admin secret from config
    :return: 404, {} if the secret code is incorrect
    200, {} if everything is dropped and recreated successfully
    """
    if secret_code != Config.ADMIN_SECRET:
        return 404, json.dumps({})
    dbm.clear_all_tables()
    return 200, json.dumps({})


@function_response
def fill_with_example(secret_code):
    """
    :param secret_code: admin secret from config
    :return: 404, {} if the secret code is incorrect
    200, {} if example fill executed successfully
    May throw other exceptions
    """
    if secret_code != Config.ADMIN_SECRET:
        return 404, json.dumps({})

    example_username = template_data.EXAMPLE_USER[0]
    dbm.insert_user(User(username=example_username), encrypt_password(template_data.EXAMPLE_USER[1]))

    example_tournament = template_data.EXAMPLE_TOURNAMENT_NAME
    dbm.insert_tournament(example_username, Tournament(name=example_tournament))

    for round_name in template_data.EXAMPLE_ROUNDS_NAMES:
        dbm.insert_round(example_username, example_tournament, round_name)

    for subround_name, round_ind in template_data.EXAMPLE_SUBROUNDS:
        dbm.insert_subround(example_username, example_tournament, template_data.EXAMPLE_ROUNDS_NAMES[round_ind],
                            subround_name)

    for word, diff in template_data.EXAMPLE_WORDS:
        dbm.insert_word(example_username, example_tournament, word, diff)

    for p1, p2, ri, sri, ind in template_data.EXAMPLE_PLAYERS:
        dbm.insert_player(example_username, example_tournament, p1, p2)
        dbm.add_pair_id_to_round(example_username, example_tournament, template_data.EXAMPLE_ROUNDS_NAMES[ri], ind)
        dbm.add_pair_id_to_subround(example_username, example_tournament, template_data.EXAMPLE_ROUNDS_NAMES[ri],
                                    template_data.EXAMPLE_SUBROUNDS[sri][0], ind)

    return 200, json.dumps({})

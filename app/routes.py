import json
from collections import Counter

from flask import request
import app.functions as functions
from app import app


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/api/v1/service/status', methods=['GET'])
def status():
    return functions.status()


@app.route('/api/v1/user/login', methods=['POST'])
def login():
    username: str = request.get_json()["username"]
    password: str = request.get_json()["password"]
    return functions.login(username, password)


@app.route('/api/v1/user/register', methods=['POST'])
def register():
    username: str = request.get_json()["username"]
    password: str = request.get_json()["password"]
    return functions.register(username, password)


@app.route('/api/v1/tournament', methods=['POST'])
def new_tournament():
    token: str = request.get_json()["token"]
    name: str = request.get_json()["name"]
    return functions.new_tournament(token, name)


@app.route('/api/v1/tournament', methods=['GET'])
def get_tournaments():
    token: str = request.get_json()["token"]
    return functions.get_tournaments(token)


@app.route('/api/v1/players', methods=['POST'])
def new_player():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    name_first: str = request.get_json()["name_first"]
    name_second: str = request.get_json()["name_second"]
    return functions.new_player(token, tournament_id, name_first, name_second)


@app.route('/api/v1/players', methods=['GET'])
def get_players():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    return functions.get_players(token, tournament_id)


@app.route('/api/v1/players', methods=['DELETE'])
def delete_player():
    token: str = request.get_json()["token"]
    pair_id: int = int(request.get_json()["pair_id"])
    return functions.delete_player(token, pair_id)


@app.route('/api/v1/words', methods=['POST'])
def new_word():
    token: str = request.get_json()["token"]
    tournament_id: int = request.get_json()["tournament_id"]
    word_text: str = request.get_json()["word_text"]
    word_difficulty: int = int(request.get_json()["word_difficulty"])
    return functions.new_word(token, tournament_id, word_text, word_difficulty)


@app.route('/api/v1/words', methods=['GET'])
def get_words():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    return functions.get_words(token, tournament_name)


@app.route('/api/v1/words', methods=['DELETE'])
def delete_word():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    word_text: str = request.get_json()["word_text"]
    return functions.delete_word(token, tournament_name, word_text)


@app.route('/api/v1/rounds', methods=['POST'])
def new_round():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_name"])
    round_name: str = request.get_json()["round_name"]
    return functions.new_round(token, tournament_id, round_name)


@app.route('/api/v1/rounds', methods=['GET'])
def get_rounds():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    return functions.get_rounds(token, tournament_name)


@app.route('/api/v1/rounds', methods=['DELETE'])
def delete_round():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    return functions.delete_round(token, tournament_name, round_name)


@app.route('/api/v1/rounds/players', methods=['POST'])
def add_player_to_round():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    pair_id: int = int(request.get_json()["player_id"])
    return functions.add_player_to_round(token, tournament_name, round_name, pair_id)


@app.route('/api/v1/rounds/players', methods=['GET'])
def get_players_from_round():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    return functions.get_players_in_round(token, tournament_name, round_name)


@app.route('/api/v1/rounds/players', methods=['DELETE'])
def delete_player_from_round():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    pair_id: int = int(request.get_json()["player_id"])
    return functions.delete_player_from_round(token, tournament_name, round_name, pair_id)


@app.route('/api/v1/subrounds', methods=['POST'])
def new_subround():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.new_subround(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/subrounds', methods=['GET'])
def get_subrounds():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    return functions.get_subrounds(token, tournament_name, round_name)


@app.route('/api/v1/subrounds', methods=['DELETE'])
def delete_subround():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.delete_subround(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/subrounds/players', methods=['POST'])
def add_player_to_subround():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    pair_id: int = int(request.get_json()["player_id"])
    return functions.add_player_to_subround(token, tournament_name, round_name, subround_name, pair_id)


@app.route('/api/v1/subrounds/players', methods=['GET'])
def get_players_from_subround():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.get_players_in_subround(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/subrounds/player', methods=['DELETE'])
def delete_player_from_subround():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    pair_id: int = int(request.get_json()["player_id"])
    return functions.delete_player_from_subround(token, tournament_name, round_name, subround_name, pair_id)


@app.route('/api/v1/subrounds/words', methods=['POST'])
def add_x_words_of_diff_y_to_subround():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    words_difficulty: int = int(request.get_json()["words_difficulty"])
    words_amount: int = int(request.get_json()["words_amount"])
    return functions.add_x_words_of_diff_y_to_subround(token, tournament_name, round_name, subround_name,
                                                       words_difficulty, words_amount)


@app.route('/api/v1/subrounds/words', methods=['GET'])
def get_subround_words():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.get_subround_words(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/subrounds/split', methods=['POST'])
def split_subround_into_games():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    games_amount: int = int(request.get_json()["games_amount"])
    return functions.split_subround_into_games(token, tournament_name, round_name, subround_name, games_amount)


@app.route('/api/v1/subrounds/games', methods=['GET'])
def get_games():  # TODO: Not really meaningful
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.get_games(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/subrounds/split', methods=['DELETE'])
def undo_split_subround_into_games():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.undo_split_subround_into_games(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/games/players', methods=['GET'])
def get_game():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    game_id: int = int(request.get_json()["game_id"])
    return functions.get_game_players(token, tournament_name, game_id)


@app.route('/api/v1/games/results', methods=['POST'])
def set_game_result():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    game_id: int = int(request.get_json()["game_id"])
    result_with_s_keys: dict = json.loads(request.get_json()["result"])
    result = Counter(dict((int(key), val) for key, val in result_with_s_keys.items()))
    return functions.set_game_result(token, tournament_name, game_id, result)


@app.route('/api/v1/games/results', methods=['GET'])
def get_game_result():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    game_id: int = int(request.get_json()["game_id"])
    return functions.get_game_result(token, tournament_name, game_id)


@app.route('/api/v1/games/results', methods=['DELETE'])
def delete_game_result():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    game_id: int = int(request.get_json()["game_id"])
    return functions.delete_game_result(token, tournament_name, game_id)


@app.route('/api/v1/subrounds/results', methods=['GET'])
def get_subround_result():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.get_subround_result(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/rounds/results', methods=['GET'])
def get_round_result():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["tournament_name"]
    round_name: str = request.get_json()["round_name"]
    return functions.get_round_result(token, tournament_name, round_name)


@app.route('/api/v1/admin/drop', methods=['DELETE'])
def drop_table():
    secret_code: str = request.get_json()["secret_code"]
    return functions.drop_tables(secret_code)


@app.route('/api/v1/admin/fill_with_example', methods=['POST'])
def fill_with_example():
    secret_code: str = request.get_json()["secret_code"]
    return functions.fill_with_example(secret_code)

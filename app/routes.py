import json
from collections import Counter
from typing import List

from flask import request
import app.functions as functions
from app import app


@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"


@app.route("/api/v1/service/status", methods=["GET"])
def status():
    return functions.status()


@app.route("/api/v1/user/login", methods=["POST"])
def login():
    username: str = request.get_json()["username"]
    password: str = request.get_json()["password"]
    return functions.login(username, password)


@app.route("/api/v1/user/register", methods=["POST"])
def register():
    username: str = request.get_json()["username"]
    password: str = request.get_json()["password"]
    return functions.register(username, password)


@app.route("/api/v1/tournament", methods=["POST"])
def new_tournament():
    token: str = request.get_json()["token"]
    name: str = request.get_json()["name"]
    return functions.new_tournament(token, name)


@app.route("/api/v1/tournaments", methods=["GET"])
def get_tournaments():
    token: str = request.get_json()["token"]
    return functions.get_tournaments(token)


@app.route("/api/v1/tournament/<tournament_id>", methods=["GET"])
def get_tournament(tournament_id: int):
    token: str = request.get_json()["token"]
    return functions.get_tournament_info(token, tournament_id)


@app.route("/api/v1/tournament", methods=["DELETE"])
def delete_tournament():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    return functions.delete_tournament(token, tournament_id)


@app.route("/api/v1/player", methods=["POST"])
def new_player():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    name_first: str = request.get_json()["name_first"]
    name_second: str = request.get_json()["name_second"]
    return functions.new_player(token, tournament_id, name_first, name_second)


@app.route("/api/v1/players", methods=["GET"])
def get_players():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    return functions.get_players(token, tournament_id)


@app.route("/api/v1/player", methods=["DELETE"])
def delete_player():
    token: str = request.get_json()["token"]
    pair_id: int = int(request.get_json()["pair_id"])
    return functions.delete_player(token, pair_id)


@app.route("/api/v1/word", methods=["POST"])
def new_word():
    token: str = request.get_json()["token"]
    tournament_id: int = request.get_json()["tournament_id"]
    word_text: str = request.get_json()["word_text"]
    word_difficulty: int = int(request.get_json()["word_difficulty"])
    return functions.new_word(token, tournament_id, word_text, word_difficulty)


@app.route("/api/v1/words", methods=["GET"])
def get_words():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    return functions.get_words(token, tournament_id)


@app.route("/api/v1/word", methods=["DELETE"])
def delete_word():
    token: str = request.get_json()["token"]
    word_id: int = int(request.get_json()["word_id"])
    return functions.delete_word(token, word_id)


@app.route("/api/v1/round", methods=["POST"])
def new_round():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    round_name: str = request.get_json()["round_name"]
    return functions.new_round(token, tournament_id, round_name)


@app.route("/api/v1/round/<round_id>", methods=["GET"])
def get_round(round_id: int):
    token: str = request.get_json()["token"]
    return functions.get_round_info(token, round_id)


@app.route("/api/v1/rounds", methods=["GET"])
def get_rounds():
    token: str = request.get_json()["token"]
    tournament_id: int = int(request.get_json()["tournament_id"])
    return functions.get_rounds(token, tournament_id)


@app.route("/api/v1/round", methods=["DELETE"])
def delete_round():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    return functions.delete_round(token, round_id)


@app.route("/api/v1/round/player", methods=["POST"])
def add_player_to_round():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    pair_id: int = int(request.get_json()["player_id"])
    return functions.add_player_to_round(token, round_id, pair_id)


@app.route("/api/v1/round/players", methods=["POST"])
def add_players_to_round():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    pair_ids: List[int] = list(map(int, request.get_json()["player_ids"]))
    return functions.add_players_to_round(token, round_id, pair_ids)


@app.route("/api/v1/round/players", methods=["GET"])
def get_players_in_round():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    return functions.get_players_in_round(token, round_id)


@app.route("/api/v1/round/player", methods=["DELETE"])
def delete_player_from_round():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    pair_id: int = int(request.get_json()["player_id"])
    return functions.delete_player_from_round(token, round_id, pair_id)


@app.route("/api/v1/subround", methods=["POST"])
def new_subround():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    subround_name: str = request.get_json()["subround_name"]
    return functions.new_subround(token, round_id, subround_name)


@app.route("/api/v1/subround/<subround_id>", methods=["GET"])
def get_subround(subround_id: int):
    token: str = request.get_json()["token"]
    return functions.get_subround_info(token, subround_id)


@app.route("/api/v1/subrounds", methods=["GET"])
def get_subrounds():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    return functions.get_subrounds(token, round_id)


@app.route("/api/v1/subround", methods=["DELETE"])
def delete_subround():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.delete_subround(token, subround_id)


@app.route("/api/v1/subround/player", methods=["POST"])
def add_player_to_subround():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    pair_id: int = int(request.get_json()["player_id"])
    return functions.add_player_to_subround(token, subround_id, pair_id)


@app.route("/api/v1/subround/players", methods=["POST"])
def add_players_to_subround():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    pair_ids: List[int] = list(map(int, request.get_json()["player_ids"]))
    return functions.add_players_to_subround(token, subround_id, pair_ids)


@app.route("/api/v1/subround/players", methods=["GET"])
def get_players_from_subround():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.get_players_in_subround(token, subround_id)


@app.route("/api/v1/subround/player", methods=["DELETE"])
def delete_player_from_subround():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    pair_id: int = int(request.get_json()["player_id"])
    return functions.delete_player_from_subround(token, subround_id, pair_id)


@app.route("/api/v1/subround/word", methods=["POST"])
def add_x_words_of_diff_y_to_subround():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    words_difficulty: int = int(request.get_json()["words_difficulty"])
    words_amount: int = int(request.get_json()["words_amount"])
    return functions.add_x_words_of_diff_y_to_subround(
        token, subround_id, words_difficulty, words_amount
    )


@app.route("/api/v1/subround/words", methods=["GET"])
def get_subround_words():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.get_subround_words(token, subround_id)


@app.route("/api/v1/subround/split", methods=["POST"])
def split_subround_into_games():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    games_amount: int = int(request.get_json()["games_amount"])
    return functions.split_subround_into_games(token, subround_id, games_amount)


@app.route("/api/v1/subround/games", methods=["GET"])
def get_games():  # TODO: Not really meaningful, idk what else to add
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.get_games(token, subround_id)


@app.route("/api/v1/subround/split", methods=["DELETE"])
def undo_split_subround_into_games():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.undo_split_subround_into_games(token, subround_id)


@app.route("/api/v1/game/<game_id>", methods=["GET"])
def get_game(game_id: int):
    token: str = request.get_json()["token"]
    return functions.get_game_info(token, game_id)


@app.route("/api/v1/game/results", methods=["POST"])
def set_game_result():
    token: str = request.get_json()["token"]
    game_id: int = int(request.get_json()["game_id"])
    result_with_s_keys: dict = json.loads(request.get_json()["result"])
    result = Counter(dict((int(key), val) for key, val in result_with_s_keys.items()))
    return functions.set_game_result(token, game_id, result)


@app.route("/api/v1/game/results", methods=["GET"])
def get_game_result():
    token: str = request.get_json()["token"]
    game_id: int = int(request.get_json()["game_id"])
    return functions.get_game_result(token, game_id)


@app.route("/api/v1/game/results/pretty", methods=["GET"])
def get_game_result_pretty():
    token: str = request.get_json()["token"]
    game_id: int = int(request.get_json()["game_id"])
    return functions.get_game_result(token, game_id, pretty=True)


@app.route("/api/v1/game/results", methods=["DELETE"])
def delete_game_result():
    token: str = request.get_json()["token"]
    game_id: int = int(request.get_json()["game_id"])
    return functions.delete_game_result(token, game_id)


@app.route("/api/v1/subround/results", methods=["GET"])
def get_subround_result():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.get_subround_result(token, subround_id)


@app.route("/api/v1/subround/results/pretty", methods=["GET"])
def get_subround_result_pretty():
    token: str = request.get_json()["token"]
    subround_id: int = int(request.get_json()["subround_id"])
    return functions.get_subround_result(token, subround_id, pretty=True)


@app.route("/api/v1/round/results", methods=["GET"])
def get_round_result():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    return functions.get_round_result(token, round_id)


@app.route("/api/v1/round/results/pretty", methods=["GET"])
def get_round_result_pretty():
    token: str = request.get_json()["token"]
    round_id: int = int(request.get_json()["round_id"])
    return functions.get_round_result(token, round_id, pretty=True)


@app.route("/api/v1/admin/drop", methods=["DELETE"])
def drop_table():
    secret_code: str = request.get_json()["secret_code"]
    return functions.drop_tables(secret_code)


@app.route("/api/v1/admin/fill_with_example", methods=["POST"])
def fill_with_example():
    secret_code: str = request.get_json()["secret_code"]
    return functions.fill_with_example(secret_code)

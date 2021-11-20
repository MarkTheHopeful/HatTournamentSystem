from entities.game import Game
from entities.round_console import Round, Subround
from entities.tournament_console import Tournament
from utils.template_data import basic_players_names, basic_words_d
from typing import List, Optional
from collections import Counter
from typing import Counter as CounterT

VERSION_INTERFACE: str = "0.0.3"
HELP: str = """
Доступные команды:
quit, exit
version
help
add word
delete word
add players
delete players
template fill
add round
add subround
checkout round
checkout subround
checkout game
set game results
split to games
conclude subround result
conclude round result
get k best
"""

if __name__ == "__main__":
    current_tournament: Tournament = Tournament(0)
    current_round: Optional[Round] = None
    current_subround: Optional[Subround] = None
    current_game: Optional[Game] = None
    print("Система организации турниров по шляпе, локальный командный интерфейс")

    while True:
        command: str = input(">>> ")
        if command == "quit" or command == "exit":
            break
        elif command == "version":
            print(f"Версия интерфейса: {VERSION_INTERFACE}")
            print(f"Версия класса: {current_tournament.VERSION}")
        elif command == "help":
            print(HELP)
        elif command == "add word":
            word: str = input("Введите слово:\n")
            difficulty: int = int(input("Введите сложность:\n"))
            result, word_id = current_tournament.add_word(word, difficulty)  # FIXME: No type annotation
            if result:
                print(f"Слово добавлено, его uid: {word_id}")
            else:
                print(f"Слово уже есть в базе")
        elif command == "delete word":
            word: str = input("Введите слово:\n")
            result: bool = current_tournament.delete_word(word)
            if result:
                print(f"Слово удалено")
            else:
                print(f"Слова нет в базе")
        elif command == "add players":
            first_player: str = input("Введите имя и фамилию первого игрока:\n")
            second_player: str = input("Введите имя и фамилию второго игрока:\n")
            result: bool = current_tournament.add_play_pair(first_player, second_player)
            if result:
                print("Пара игроков успешно добавлена")
            else:
                print("Пара игроков уже участвует")
        elif command == "delete players":
            first_player: str = input("Введите имя и фамилию первого игрока:\n")
            second_player: str = input("Введите имя и фамилию второго игрока:\n")
            result: bool = current_tournament.delete_play_pair(first_player, second_player)
            if result:
                print("Пара игроков успешно удалена")
            else:
                print("Пары игроков нет в списке участников")
        elif command == "template fill":
            for word, diff in basic_words_d:
                current_tournament.add_word(word, diff)
            for play_1, play_2 in basic_players_names:
                current_tournament.add_play_pair(play_1, play_2)
            print("Добавлены слова и игроки для примера")
        elif command == "add round":
            players_uid: List[int] = list(map(int, input("Введите uid пар участников нового раунда:\n").split()))
            difficulty: int = int(input("Введите ожидаемую сложность раунда:\n"))
            name: str = input("Введите название раунда:\n")
            current_tournament.create_round(players_uid, difficulty, name)
            print("Раунд создан")
        elif command == "checkout round":
            round_id: int = int(input("Введите номер раунда:\n"))
            if round_id >= len(current_tournament.rounds):
                print("Нет раунда с таким номером")
            else:
                current_round = current_tournament.rounds[round_id]
                print("Раунд успешно выбран")
        elif command == "add subround":
            if current_round is None:
                print("Сначала выберите раунд")
                continue
            players_uid: List[int] = list(map(int, input("Введите uid пар участников нового подраунда:\n").split()))
            words_amount: int = int(input("Укажите, сколько слов из банка взять:\n"))
            result: bool = current_round.add_subround(players_uid, words_amount)
            if result:
                print("Подраунд успешно создан")
            else:
                print("Что-то пошло не так")
        elif command == "checkout subround":
            if current_round is None:
                print("Сначала выберите раунд")
                continue
            subround_id: int = int(input("Введите номер подраунда:\n"))
            if subround_id >= len(current_round.subrounds):
                print("Нет подраунда с таким номером")
            else:
                current_subround = current_round.subrounds[subround_id]
                print("Подраунд успешно выбран")
        elif command == "split to games":
            if current_subround is None:
                print("Сначала выберите подраунд")
                continue
            games_amount: int = int(input("Укажите, на сколько игр разбить подраунд:\n"))
            result: bool = current_subround.split_players_to_games(games_amount)
            if result:
                print("Подраунд успешно разбит на игры")
            else:
                print("Что-то пошло не так")
        elif command == "checkout game":
            if current_subround is None:
                print("Сначала выберите подраунд")
                continue
            game_id: int = int(input("Введите номер игры:\n"))
            if game_id >= len(current_subround.games):
                print("Нет игры с таким номером")
            else:
                current_game = current_subround.games[game_id]
                print("Игра успешно выбрана")
        elif command == "set game results":
            if current_game is None:
                print("Сначала выберите игру")
                continue
            game_results: CounterT[int] = Counter(current_game.participants_uid)
            for player_uid in current_game.participants_uid:
                game_results[player_uid] = int(
                    input(f"Enter result for pair {current_tournament.uid_to_play_pair[player_uid]}:\n"))

            result: bool = current_game.conclude_result(game_results)
            if result:
                print("Итоги успешно подведены")
            else:
                print("Произошла какая-то ошибка при подведении итогов")
        elif command == "conclude subround result":
            result: bool = current_subround.conclude_results()
            if result:
                print("Итоги подраунда успешно подведены")
            else:
                print("Подведение итогов не прошло успешно")
        elif command == "conclude round result":
            result: bool = current_round.conclude_results()
            if result:
                print("Итоги раунда успешно подведены")
            else:
                print("Подведение итогов не прошло успешно")
        elif command == "get k best":
            k: int = int(input("Укажите число для взятия:\n"))
            result: Optional[List[int]] = current_round.get_top_n(k)
            if result:
                for uid in result:
                    print(current_tournament.uid_to_play_pair[uid])
            else:
                print("Что-то пошло не так")

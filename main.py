from tournament import Tournament

VERSION_INTERFACE: str = "0.0.1"
HELP: str = """
Доступные команды:
quit, exit
version
help
add word
delete word
add players
delete players
"""

if __name__ == "__main__":
    current_tournament: Tournament = Tournament(0)
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

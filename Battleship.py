from random import randint
from time import sleep


class BoardException(Exception):
    pass


class OutOfBoundsException(BoardException):
    def __str__(self):
        return "Координаты указывают за пределы игрового поля"


class RepitedShotException(BoardException):
    def __str__(self):
        return "Выстрел в эту точку уже был произведен"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, orient, bow, deck):
        self.orient = orient  # Ориентация корабля
        self.bow = bow  # Координаты носа корабля
        self.deck = deck  # Кол-во палуб судна
        self.lives = deck  # Через сколько попаданий утонет посудина (кол-во жизней)

    def dots(self):
        ship_dots = []
        for i in range(self.deck):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orient == 0:
                cur_x += i

            elif self.orient == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    board_size = '6x6'  # справочные данные
    board_empty = ([" ", "1", "2", "3", "4", "5", "6"],
                   ["1", "░", "░", "░", "░", "░", "░"],
                   ["2", "░", "░", "░", "░", "░", "░"],
                   ["3", "░", "░", "░", "░", "░", "░"],
                   ["4", "░", "░", "░", "░", "░", "░"],
                   ["5", "░", "░", "░", "░", "░", "░"],
                   ["6", "░", "░", "░", "░", "░", "░"])

    def __init__(self, hide=False):
        self.board = ([" ", "1", "2", "3", "4", "5", "6"],
                      ["1", "░", "░", "░", "░", "░", "░"],
                      ["2", "░", "░", "░", "░", "░", "░"],
                      ["3", "░", "░", "░", "░", "░", "░"],
                      ["4", "░", "░", "░", "░", "░", "░"],
                      ["5", "░", "░", "░", "░", "░", "░"],
                      ["6", "░", "░", "░", "░", "░", "░"])
        self.hide = hide

        self.busy = []
        self.ships = []
        self.live_ships = 7

    def for_printer(self):
        return self.board

    def __str__(self):
        print_board = self.board
        if self.hide:
            for row in print_board:
                for col in range(1, 7):
                    if row[col] == "■":
                        row[col] = "░"
            print("Поле противника:")
            print("___________________________")
            for row in print_board:
                print(" | ".join(row[0:7]) + " |")
                print("___________________________")
        if not self.hide:
            print("Ваше поле:")
            print("___________________________")
            for row in print_board:
                print(" | ".join(row[0:7]) + " |")
                print("___________________________")
        return "          ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬"

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, 1), (0, 0), (0, -1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots():
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.board[cur.x][cur.y] = "○"
                    self.busy.append(cur)

    def add_ship(self, ship):

        for d in ship.dots():
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots():
            self.board[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def out(self, d):
        return not ((0 < d.x < 7) and (0 < d.y < 7))

    def shot(self, d):
        if self.out(d):
            raise OutOfBoundsException
            #print("Координаты указывают за пределы игрового поля")
            #return True

        if d in self.busy:
            raise RepitedShotException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots():
                ship.lives -= 1
                self.board[d.x][d.y] = "¤"
                if ship.lives == 0:
                    self.live_ships -= 1
                    self.contour(ship, True)
                    print("Корабль уничтожен")
                    sleep(2)
                    return True
                else:
                    print("Корабль ранен, дополнительный ход")
                    sleep(2)
                    return True
        self.board[d.x][d.y] = "○"
        print("Мимо")
        sleep(2)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class User(Player):
    def ask(self):
        while True:
            print("Ваш ход:")
            cord_x = input("Номер строки - ")
            cord_y = input("Номер столбца - ")
            if not (cord_x.isdigit()) or not (cord_y.isdigit()):
                print("Введите числа")
                continue
            cord_x = int(cord_x)
            cord_y = int(cord_y)
            return Dot(cord_x, cord_y)


class AI(Player):
    def ask(self):
        d = Dot(randint(1, 6), randint(1, 6))
        print(f"Компьютер бьет в точку {d.x} {d.y}")
        return d


class Game:
    def gen_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(randint(0, 1), Dot(randint(1, 6), randint(1, 6)), l)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.gen_board()
        return board

    def __init__(self):
        pl = self.random_board()
        ai = self.random_board()
        ai.hide = True

        self.us = User(pl, ai)
        self.ai = AI(ai, pl)

    def greet(self):
        print('''        ┌───────────────────────────┐
        │     Добро пожаловать!     │
        │     Игра "Морской бой"    │
        │ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ │
        │   Твоя задача: победить   │
        │    противника, до того,   │
        │ как он сделает это первый │
        │ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ │
        │     Доска генерируется    │
        │    автоматически, тебе    │
        │   нужно только атаковать  │
        │ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ │
        │       Удачного боя!       │
        └───────────────────────────┘''')

    def loop(self):
        num = 0
        while True:
            print("          ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬")
            print(self.us.board)
            sleep(1)
            print(self.ai.board)
            sleep(1)
            if num % 2 == 0:
                print('Игрок, твой ход!')
                repeat = self.us.move()
            else:
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.us.board.live_ships == 0:
                print('''          ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ 
            Ты проиграл! В следующий раз повезет!''')
                sleep(5)
                break

            if self.ai.board.live_ships == 0:
                print('''          ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ 
                Поздравляю, ты выиграл!''')
                sleep(5)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()

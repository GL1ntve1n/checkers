from tkinter import Canvas, Event, messagebox
from PIL import Image, ImageTk
from random import choice
from pathlib import Path
from time import sleep
from math import inf

from checkers.field import Field
from checkers.move import Move
from checkers.constants import *
from checkers.enums import CheckerType, SideType

#Класс игры
class Game:
    def __init__(self, canvas: Canvas, x_field_size: int, y_field_size: int, exit_callback):
        self.__canvas = canvas
        self.__field = Field(x_field_size, y_field_size)

        self.__player_turn = True

        self.__exit_callback = exit_callback

        self.__hovered_cell = Point()
        self.__selected_cell = Point()
        self.__animated_cell = Point()

        self.__init_images()
        
        self.__draw()

        # Если игрок играет за чёрных, то совершить ход противника
        if PLAYER_SIDE == SideType.BLACK:
            self.__handle_enemy_turn()

    # Инициализация изображений
    def __init_images(self):
        self.__images = {
            CheckerType.WHITE_REGULAR: ImageTk.PhotoImage(Image.open(Path('assets', 'white-regular.png')).resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)),
            CheckerType.BLACK_REGULAR: ImageTk.PhotoImage(Image.open(Path('assets', 'black-regular.png')).resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)),
            CheckerType.WHITE_QUEEN: ImageTk.PhotoImage(Image.open(Path('assets', 'white-queen.png')).resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)),
            CheckerType.BLACK_QUEEN: ImageTk.PhotoImage(Image.open(Path('assets', 'black-queen.png')).resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)),
        }

    #Анимация перемещения шашки
    def __animate_move(self, move: Move):
        self.__animated_cell = Point(move.from_x, move.from_y)
        self.__draw()

        # Создание шашки для анимации
        animated_checker = self.__canvas.create_image(move.from_x * CELL_SIZE, move.from_y * CELL_SIZE, image=self.__images.get(self.__field.type_at(move.from_x, move.from_y)), anchor='nw', tag='animated_checker')
        
        # Вектора движения
        dx = 1 if move.from_x < move.to_x else -1
        dy = 1 if move.from_y < move.to_y else -1

        # Анимация
        for distance in range(abs(move.from_x - move.to_x)):
            for _ in range(100 // ANIMATION_SPEED):
                self.__canvas.move(animated_checker, ANIMATION_SPEED / 100 * CELL_SIZE * dx, ANIMATION_SPEED / 100 * CELL_SIZE * dy)
                self.__canvas.update()
                sleep(0.01)

        self.__animated_cell = Point()
    #Отрисовка сетки поля и шашек
    def __draw(self):
        self.__canvas.delete('all')
        self.__draw_field_grid()
        self.__draw_checkers()
        self.__draw_turn()

    # Отрисовка чей ход
    def __draw_turn(self):
        if self.__player_turn:
            self.__canvas.create_text(
                self.__field.x_size * CELL_SIZE // 2,
                self.__field.y_size * CELL_SIZE + 15,
                text='Ваш ход',
                anchor='center',
                fill='green'
            )
        else:
            self.__canvas.create_text(
                self.__field.x_size * CELL_SIZE // 2,
                self.__field.y_size * CELL_SIZE + 15,
                text='Ход соперника',
                anchor='center',
                fill='red'
            )
    #Отрисовка сетки поля
    def __draw_field_grid(self):
        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                self.__canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, x * CELL_SIZE + CELL_SIZE, y * CELL_SIZE + CELL_SIZE, fill=FIELD_COLORS[(y + x) % 2], width=0, tag='boards')

                # Отрисовка рамок у необходимых клеток
                if x == self.__selected_cell.x and y == self.__selected_cell.y:
                    self.__canvas.create_rectangle(x * CELL_SIZE + BORDER_WIDTH // 2, y * CELL_SIZE + BORDER_WIDTH // 2, x * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2, y * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2, outline=SELECT_BORDER_COLOR, width=BORDER_WIDTH, tag='border')
                elif x == self.__hovered_cell.x and y == self.__hovered_cell.y:
                    self.__canvas.create_rectangle(x * CELL_SIZE + BORDER_WIDTH // 2, y * CELL_SIZE + BORDER_WIDTH // 2, x * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2, y * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2, outline=HOVER_BORDER_COLOR,  width=BORDER_WIDTH, tag='border')

                # Отрисовка возможных точек перемещения, если есть выбранная ячейка
                if self.__selected_cell:
                    player_moves_list = self.__get_moves_list(PLAYER_SIDE)
                    for move in player_moves_list:
                        if self.__selected_cell.x == move.from_x and self.__selected_cell.y == move.from_y:
                            self.__canvas.create_oval(move.to_x * CELL_SIZE + CELL_SIZE / 3, move.to_y * CELL_SIZE + CELL_SIZE / 3, move.to_x * CELL_SIZE + (CELL_SIZE - CELL_SIZE / 3), move.to_y * CELL_SIZE + (CELL_SIZE - CELL_SIZE / 3), fill=POSIBLE_MOVE_CIRCLE_COLOR, width=0, tag='posible_move_circle' )

    # Отрисовка шашек
    def __draw_checkers(self):
        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                # Не отрисовывать пустые ячейки и анимируемую шашку
                if self.__field.type_at(x, y) != CheckerType.NONE and not (x == self.__animated_cell.x and y == self.__animated_cell.y):
                    self.__canvas.create_image(x * CELL_SIZE, y * CELL_SIZE, image=self.__images.get(self.__field.type_at(x, y)), anchor='nw', tag='checkers')

    # Событие перемещения мышки
    def mouse_move(self, event: Event):
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        if x != self.__hovered_cell.x or y != self.__hovered_cell.y:
            self.__hovered_cell = Point(x, y)

            # Если ход игрока, то перерисовать
            if self.__player_turn:
                self.__draw()

    # Событие нажатия мышки
    def mouse_down(self, event: Event):
        if not self.__player_turn: return

        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE

        # Если точка не внутри поля
        if not (self.__field.is_within(x, y)):
            return

        if PLAYER_SIDE == SideType.WHITE:
            player_checkers = WHITE_CHECKERS
        elif PLAYER_SIDE == SideType.BLACK:
            player_checkers = BLACK_CHECKERS
        else:
            return

        # Если нажатие по шашке игрока, то выбрать её
        if self.__field.type_at(x, y) in player_checkers:
            self.__selected_cell = Point(x, y)
            self.__draw()
        elif self.__player_turn:
            move = Move(self.__selected_cell.x, self.__selected_cell.y, x, y)

            # Если нажатие по ячейке, на которую можно походить
            if move in self.__get_moves_list(PLAYER_SIDE):
                self.__handle_player_turn(move)

                # Если не ход игрока, то ход противника
                if not self.__player_turn:
                    self.__handle_enemy_turn()

    # Совершение хода
    def __handle_move(self, move: Move, draw: bool = True) -> bool:
        if draw:
            self.__animate_move(move)

        # Изменение позиции шашки
        if self.__field.at(move.from_x, move.from_y).type != CheckerType.NONE:
            self.__field.at(move.to_x, move.to_y).change_type(self.__field.type_at(move.from_x, move.from_y))
            self.__field.at(move.from_x, move.from_y).change_type(CheckerType.NONE)

        # Вектора движения
        dx = -1 if move.from_x < move.to_x else 1
        dy = -1 if move.from_y < move.to_y else 1

        # Удаление съеденных шашек
        has_killed_checker = False
        x, y = move.to_x, move.to_y
        while x != move.from_x or y != move.from_y:
            x += dx
            y += dy
            if self.__field.type_at(x, y) != CheckerType.NONE:
                self.__field.at(x, y).change_type(CheckerType.NONE)
                has_killed_checker = True

        # Изменение типа шашки, если она дошла до края, но только если на этом завершился её ход
        if not has_killed_checker or not self.__get_required_moves_list(
            SideType.BLACK if self.__field.type_at(move.to_x, move.to_y) in BLACK_CHECKERS else SideType.WHITE,
            move
        ):
            if move.to_y == 0 and self.__field.type_at(move.to_x, move.to_y) == CheckerType.WHITE_REGULAR:
                self.__field.at(move.to_x, move.to_y).change_type(CheckerType.WHITE_QUEEN)
            elif move.to_y == self.__field.y_size - 1 and self.__field.type_at(move.to_x,
                                                                               move.to_y) == CheckerType.BLACK_REGULAR:
                self.__field.at(move.to_x, move.to_y).change_type(CheckerType.BLACK_QUEEN)

        if draw:
            self.__draw()

        return has_killed_checker

    # Обработка хода игрока
    def __handle_player_turn(self, move: Move):
        self.__player_turn = False

        # Была ли убита шашка
        has_killed_checker = self.__handle_move(move)

        required_moves_list = list(filter(lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y, self.__get_required_moves_list(PLAYER_SIDE)))
        
        # Если есть ещё ход этой же шашкой
        if has_killed_checker and required_moves_list:
            self.__player_turn = True

        self.__selected_cell = Point()

    # Обработка хода противка(компьютера)
    def __handle_enemy_turn(self):
        self.__player_turn = False

        for move in self.__minimax_move(4, -float('inf'), float('inf'), PLAYER_SIDE.opposite())[1]:
            if not self.__handle_move(move) or not self.__get_required_moves_list(PLAYER_SIDE.opposite(), move):
                break
            
        self.__player_turn = True
        
        self.__check_for_game_over()

    # Проверка на конец игры
    def __check_for_game_over(self):
        game_over = False

        white_moves_list = self.__get_moves_list(SideType.WHITE)
        if not white_moves_list:
            # Белые проиграли
            answer = messagebox.showinfo('Конец игры', 'Чёрные выиграли')
            game_over = True

        black_moves_list = self.__get_moves_list(SideType.BLACK)
        if not black_moves_list:
            # Чёрные проиграли
            answer = messagebox.showinfo('Конец игры', 'Белые выиграли')
            game_over = True
        
        if game_over:
            # Новая игра
            self.__init__(self.__canvas, self.__field.x_size, self.__field.y_size, self.__exit_callback)
    #алгоритм минимакс возвращает оценку хода и список лучших ходов
    def __minimax_move(self, depth: int, alpha: float, beta: float, side: SideType) -> (float, list[Move]):
        if depth == 0 or self.__field.black_score == 0 or self.__field.white_score == 0:
            try:
                return self.__field.white_score / float(self.__field.black_score) \
                       if PLAYER_SIDE == SideType.BLACK \
                       else self.__field.black_score / float(self.__field.white_score), []
            except ZeroDivisionError:
                return float('inf'), []

        if side == PLAYER_SIDE.opposite():
            max_value = -float("inf")
            max_move = []
            field_copy = Field.copy(self.__field)
            for move in self.__get_moves_list(side):
                killed = self.__handle_move(move, False) and bool(self.__get_required_moves_list(side, move))
                eval, seq_moves = self.__minimax_move(depth - 1 if not killed else depth, alpha, beta, side.opposite() if not killed else side)
                if eval > max_value:
                    max_value = eval
                    max_move = [move] + seq_moves
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                self.__field = Field.copy(field_copy)
            return max_value, max_move
        else:
            min_value = float("inf")
            min_move = []
            field_copy = Field.copy(self.__field)
            for move in self.__get_moves_list(side):
                killed = self.__handle_move(move, False) and bool(self.__get_required_moves_list(side, move))
                eval, seq_moves = self.__minimax_move(depth - 1 if not killed else depth, alpha, beta,
                                                      side.opposite() if not killed else side)
                if eval < min_value:
                    min_value = eval
                    min_move = [move] + seq_moves
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                self.__field = Field.copy(field_copy)
            return min_value, min_move

    #Получение списка ходов
    def __get_moves_list(self, side: SideType, from_move: Move = None) -> list[Move]:
        moves_list = self.__get_required_moves_list(side, from_move=from_move)

        if self.__player_turn:
            moves_and_evaluate = list(zip(moves_list, (self.__evaluate_move(move) for move in moves_list)))
            moves_and_evaluate = sorted(moves_and_evaluate, key=lambda m: m[1], reverse=True)
            moves_list = list(map(lambda m: m[0], filter(lambda x: x[1] == moves_and_evaluate[0][1], moves_and_evaluate)))

        if not moves_list:
            moves_list = self.__get_optional_moves_list(side)
        return moves_list

    #Оценка хода, насколько много вражеских шашек можно съесть, совершив указанный ход
    def __evaluate_move(self, move: Move) -> int:
        field_copy = Field.copy(self.__field)

        killed = self.__handle_move(move, False)

        value = int(killed) + max(list(self.__evaluate_move(m) for m in self.__get_required_moves_list(PLAYER_SIDE, move)) + [0])

        self.__field = field_copy

        return value

    #Получение списка обязательных ходов
    def __get_required_moves_list(self, side: SideType, from_move: Move = None) -> list[Move]:
        moves_list = []

        # Определение типов шашек
        if side == SideType.WHITE:
            friendly_checkers = WHITE_CHECKERS
            enemy_checkers = BLACK_CHECKERS
        elif side == SideType.BLACK:
            friendly_checkers = BLACK_CHECKERS
            enemy_checkers = WHITE_CHECKERS
        else:
            return moves_list

        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):

                # Для обычной шашки
                if self.__field.type_at(x, y) == friendly_checkers[0]:
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x * 2, y + offset.y * 2)):
                            continue

                        if self.__field.type_at(x + offset.x, y + offset.y) in enemy_checkers and self.__field.type_at(x + offset.x * 2, y + offset.y * 2) == CheckerType.NONE:
                            moves_list.append(Move(x, y, x + offset.x * 2, y + offset.y * 2))

                # Для дамки
                elif self.__field.type_at(x, y) == friendly_checkers[1]:
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x * 2, y + offset.y * 2)):
                            continue

                        has_enemy_checker_on_way = False

                        for shift in range(1, self.__field.size):
                            if not (self.__field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            # Если на пути не было вражеской шашки
                            if not has_enemy_checker_on_way:
                                if self.__field.type_at(x + offset.x * shift, y + offset.y * shift) in enemy_checkers:
                                    has_enemy_checker_on_way = True
                                    continue
                                # Если на пути союзная шашка - то закончить цикл
                                elif self.__field.type_at(x + offset.x * shift, y + offset.y * shift) in friendly_checkers:
                                    break
                            
                            # Если на пути была вражеская шашка
                            if has_enemy_checker_on_way:
                                if self.__field.type_at(x + offset.x * shift, y + offset.y * shift) == CheckerType.NONE:
                                    moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                                else:
                                    break
                            
        return list(filter(
            lambda m: from_move.to_x == m.from_x and from_move.to_y == m.from_y,
            moves_list
        )) if from_move else moves_list

    #Получение списка необязательных ходов
    def __get_optional_moves_list(self, side: SideType) -> list[Move]:
        moves_list = []

        # Определение типов шашек
        if side == SideType.WHITE:
            friendly_checkers = WHITE_CHECKERS
        elif side == SideType.BLACK:
            friendly_checkers = BLACK_CHECKERS
        else:
            return moves_list

        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                # Для обычной шашки
                if self.__field.type_at(x, y) == friendly_checkers[0]:
                    for offset in MOVE_OFFSETS[:2] if side == SideType.WHITE else MOVE_OFFSETS[2:]:
                        if not self.__field.is_within(x + offset.x, y + offset.y):
                            continue

                        if self.__field.type_at(x + offset.x, y + offset.y) == CheckerType.NONE:
                            moves_list.append(Move(x, y, x + offset.x, y + offset.y))

                # Для дамки
                elif self.__field.type_at(x, y) == friendly_checkers[1]:
                    for offset in MOVE_OFFSETS:
                        if not self.__field.is_within(x + offset.x, y + offset.y):
                            continue

                        for shift in range(1, self.__field.size):
                            if not self.__field.is_within(x + offset.x * shift, y + offset.y * shift):
                                continue

                            if self.__field.type_at(x + offset.x * shift, y + offset.y * shift) == CheckerType.NONE:
                                moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                            else:
                                break

        return moves_list

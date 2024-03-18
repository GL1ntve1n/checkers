import sys
from tkinter import Tk, Canvas, PhotoImage

from PyQt6.QtWidgets import QApplication

from checkers.game import Game
from checkers.constants import X_SIZE, Y_SIZE, CELL_SIZE
from lk.auth_gui import AuthWindow
from lk.lk_gui import LkWindow


# функиця начала игры
def start_game():
    # Создание окна
    main_window = Tk()
    main_window.title(f'Канадские шашки')
    main_window.resizable(False, False)
    main_window.iconphoto(False, PhotoImage(file='icon.png'))

    # Создание холста
    main_canvas = Canvas(main_window, width=CELL_SIZE * X_SIZE, height=CELL_SIZE * Y_SIZE + 30)
    main_canvas.pack()

    game = Game(main_canvas, X_SIZE, Y_SIZE, lambda: main_window.destroy())

    main_canvas.bind("<Motion>", game.mouse_move)
    main_canvas.bind("<Button-1>", game.mouse_down)
    main_window.mainloop()

#точка входа
def main():
    app = QApplication(sys.argv)
    lk_window = LkWindow(start_game)
    auth_window = AuthWindow(lk_window)
    lk_window.set_exit_callback(lambda: [lk_window.hide(), auth_window.show()])
    auth_window.show()
    app.exec()


# Точка входа
if __name__ == '__main__':
    main()

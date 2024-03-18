from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget


class LkWindow(QMainWindow):
    def __init__(self, start_game_callback):
        super().__init__()

        self.setWindowTitle('Личный кабинет')
        self.setFixedSize(300, 200)

        self.start_game = start_game_callback

        central_widget = QLabel()
        central_widget.setPixmap(QPixmap("assets/background.png"))
        layout = QVBoxLayout()

        start_game_button = QPushButton('Начать игру')
        start_game_button.clicked.connect(lambda: [self.hide(), self.start_game(), self.show()])

        self.exit_button = QPushButton('Выйти')

        layout.addWidget(start_game_button)
        layout.addWidget(self.exit_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    #выход из личного кабинета
    def set_exit_callback(self, callback):
        self.exit_button.clicked.connect(callback)
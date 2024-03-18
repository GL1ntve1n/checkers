import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget

from lk.auth import register, authenticate, user_exist


#Класс окна авторизации/регистрации
class AuthWindow(QMainWindow):
    # Конструктор
    def __init__(self, lk_window):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)

        self.lk_window = lk_window
        self.authenticated = False

        central_widget = QLabel()
        central_widget.setPixmap(QPixmap("assets/background.png"))
        layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()

        # Виджеты окна авторизации
        login_widget = QWidget()
        login_layout = QVBoxLayout()
        self.username_login_edit = QLineEdit()
        self.password_login_edit = QLineEdit()
        self.password_login_edit.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton("Авторизация")
        login_button.clicked.connect(self.authenticate_user)
        register_button = QPushButton("Перейти к регистрации")
        register_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        login_layout.addWidget(QLabel("Имя пользователя:"))
        login_layout.addWidget(self.username_login_edit)
        login_layout.addWidget(QLabel("Пароль:"))
        login_layout.addWidget(self.password_login_edit)
        login_layout.addWidget(login_button)
        login_layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignRight)
        login_widget.setLayout(login_layout)

        #Виджеты окна регистрации
        register_widget = QWidget()
        register_layout = QVBoxLayout()
        self.username_register_edit = QLineEdit()
        self.password_register_edit = QLineEdit()
        self.password_register_edit.setEchoMode(QLineEdit.EchoMode.Password)
        register_button = QPushButton("Регистрация")
        register_button.clicked.connect(self.register_user)
        login_button = QPushButton("Перейти к авторизации")
        login_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        register_layout.addWidget(QLabel("Имя пользователя:"))
        register_layout.addWidget(self.username_register_edit)
        register_layout.addWidget(QLabel("Пароль:"))
        register_layout.addWidget(self.password_register_edit)
        register_layout.addWidget(register_button)
        register_layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignRight)
        register_widget.setLayout(register_layout)

        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)

        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # Функция авторизации
    def authenticate_user(self):
        username = self.username_login_edit.text()
        password = self.password_login_edit.text()

        if authenticate(username, password):
            QMessageBox.information(self, "Успешно", "Авторизация прошла успешно!")

            self.username_login_edit.setText('')
            self.password_login_edit.setText('')

            self.authenticated = True
            self.hide()
            self.lk_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")

    # Функция регистрации
    def register_user(self):
        username = self.username_register_edit.text()
        password = self.password_register_edit.text()

        if not username or not password:
            return QMessageBox.warning(self, "Ошибка", "Необходимо заполнить все поля!")

        if len(username) < 3 or len(username) > 20:
            return QMessageBox.warning(self, "Ошибка", "Имя пользователя должно иметь длину от 3 до 20 символов")

        if len(password) < 3 or len(password) > 20:
            return QMessageBox.warning(self, "Ошибка", "Пароль должен иметь длину от 3 до 20 символов")

        if user_exist(username):
            return QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует")


        try:
            register(username, password)
            QMessageBox.information(self, "Успешно", "Регистрация прошла успешно!")
            self.stacked_widget.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

#Точка входа
if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec())

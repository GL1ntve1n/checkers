from pathlib import Path

from lk.cypher import encrypt, decrypt

# Путь к файлу с данными пользователей
USER_DATA_PATH = Path('users.data')

#Регистрация нового пользователя
def register(username, password):
    user_data = f"{encrypt(username)}:{encrypt(password)}\n"

    with USER_DATA_PATH.open('a', encoding='utf8') as file:
        file.write(user_data)

#Авторизация пользователя
def authenticate(username, password):
    #если файл отсутствует
    if not USER_DATA_PATH.exists():
        return False
    #если файл открылся
    with USER_DATA_PATH.open('r', encoding='utf8') as file:
        for line in file:
            encrypted_username, encrypted_password = line.strip().split(':')
            if username == decrypt(encrypted_username) and password == decrypt(encrypted_password):
                return True
    return False

def user_exist(username):
    if not USER_DATA_PATH.exists():
        return False
    # если файл открылся
    with USER_DATA_PATH.open('r', encoding='utf8') as file:
        for line in file:
            encrypted_username, _ = line.strip().split(':')
            if username == decrypt(encrypted_username):
                return True
    return False

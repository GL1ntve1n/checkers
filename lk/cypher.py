secret_key = "keykey"

#Алгоритм Виженера
def vigenere(text: str, key: str, encrypt=True):
    result = ""
    for i in range(len(text)):
        letter_n = ord(text[i])
        key_n = ord(key[i % len(key)])
        if encrypt:
            value = (letter_n + key_n) % 1114112
        else:
            value = (letter_n - key_n) % 1114112
        result += chr(value)
    return result

#Функиця Шифрования
def encrypt(text: str):
    return vigenere(text=text, key=secret_key, encrypt=True)

#Функция Дешифрования
def decrypt(text: str):
    return vigenere(text=text, key=secret_key, encrypt=False)

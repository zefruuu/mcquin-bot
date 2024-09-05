import sqlite3
import random
from telebot import TeleBot
from Tokens import client_tok
import threading

TOKEN = client_tok.key
bot = TeleBot(TOKEN)


user_command_count = {}


def init_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 10  -- Начальный баланс 10 монет
        )
    ''')
    conn.commit()
    conn.close()


def get_user_balance(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, 10))  # Стартовый баланс 10 монет
        conn.commit()
        balance = 10
    else:
        balance = result[0]
    conn.close()
    return balance


def update_user_balance(user_id, amount):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()


def add_coin_every_2_hours():
    try:
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            users = cursor.fetchall()
            for user in users:
                user_id = user[0]
            update_user_balance(user_id, 1)
            print(f"Добавлена 1 монетка пользователю {user_id}")
            conn.close()    



threading.Timer(7200, add_coin_every_2_hours).start()


add_coin_every_2_hours()

# Команда для отображения баланса пользователя
@bot.message_handler(commands=['balance'])
def show_balance(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    bot.send_message(message.chat.id, f'Ваш баланс: {balance} монеток💰')

# Команда для получения картинки
@bot.message_handler(commands=['get_image'])
def get_image(message):
    user_id = message.from_user.id

    # Получаем баланс пользователя
    balance = get_user_balance(user_id)

    if balance >= 2:
        update_user_balance(user_id, -2)  # Снимаем две монетки
        send_random_image(message)  # Отправляем изображение
    else:
        bot.send_message(message.chat.id, f"""Бесплатные шуточки про мамашу закончились, жди или пополняй баланс
Ваш баланс: {balance} монеток💰 """)

# Функция для отправки случайной картинки
def send_random_image(message):
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image FROM images ORDER BY RANDOM() LIMIT 1')
    image = cursor.fetchone()
    conn.close()

    if image:
        bot.send_photo(message.chat.id, image[0])
    else:
        bot.send_message(message.chat.id, 'No images in the database')

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        """Оу да, Маквин готов!🚘
Хочешь получить шуточки про мамашу пиши - /get_image 🌼 
Посмотреть баланс монеток - /balance


Заказ телграмм/дискорд бота - @zefruuu"""
    )
  #donat
@bot.message_handler(commands=['donate'])
def donat(message):
        bot.send_message(
                message.chat.id,
                    """💸Донат💸
                    
40 монеток💰(20 картинок) - 40 руб/20 грн/230 тенге/0.5 долларов
80 монеток💰(40 картинок) - 75 руб/30 грн/500 тенге/0.7 долларов"""

        )

        # donat
@bot.message_handler(commands=['help'])
def hellp(message):
            bot.send_message(
            message.chat.id,
                """🆘Помощь🆘
                
/get_image - получить картинку️🖼
/balance - ваш баланс монеток👛
/start - перезапуск бота🔄
/help - все команды▶️"""
            )

# Команда для добавления монет
@bot.message_handler(commands=['addmoney'])
def add_money(message):
    try:
        user_id = message.from_user.id
        amount = int(message.text.split()[1])
        update_user_balance(user_id, amount)

        new_balance = get_user_balance(user_id)
        bot.send_message(message.chat.id, f'Монеты добавленны, Люблю илюшу')
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, '/addmoney <количество>')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')





# Инициализация базы данных при старте бота
init_db()

# Запуск бота
bot.infinity_polling()



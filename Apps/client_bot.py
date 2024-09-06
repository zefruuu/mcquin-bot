import sqlite3
import random
import types

from telebot import TeleBot
from Tokens import client_tok
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import threading
import time

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
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, 10)) 
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

def add_coin_every_2_hours(stop_timer):
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()
        for user in users:
            user_id = user[0]
            balance = get_user_balance(user_id)
            if balance < 100:
                update_user_balance(user_id, 1)
                print(f"+ 1 social credit💳 for {user_id}")
            else:
                print(f"Добавлено {user_id} ")
                stop_timer.set()
        conn.close()
    except ValueError:
        print('error')

def run_add_coin(stop_timer):
    while True:
        if not stop_timer.is_set():
            add_coin_every_2_hours(stop_timer)
            time.sleep(5) #тайм кароч
        else:
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE balance < 100')
            users = cursor.fetchall()
            if users:
                stop_timer.clear()
            conn.close()
            time.sleep(7200) #тайм кароч якщо чел свинка

stop_timer = threading.Event()
thread = threading.Thread(target=run_add_coin, args=(stop_timer,))
thread.daemon = True
thread.start()


@bot.message_handler(commands=['balance'])
def show_balance(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    bot.send_message(message.chat.id, f'Ваш баланс: {balance} монеток💰')

# Команда для получения картинки
@bot.message_handler(commands=['get_image'])
def get_image(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)

    if balance >= 2:
        update_user_balance(user_id, -2)
        send_random_image_with_buttons(message)
    else:
        bot.send_message(message.chat.id, f"""Бесплатные шуточки про мамашу закончились, 
каждые 2 часа возобновляеться 1 монетка! 
Стоимость 1 картинки - 2 монетки
Ваш баланс: {balance} монеток💰 """)


def send_random_image_with_buttons(message):
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image FROM images ORDER BY RANDOM() LIMIT 1')
    image = cursor.fetchone()
    conn.close()

    if image:
        # Создаем кнопки
        markup = InlineKeyboardMarkup()
        next_button = InlineKeyboardButton("Следующая картинка", callback_data="next_image")
        markup.add(next_button)


        bot.send_photo(message.chat.id, image[0], reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'No images in the database')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id
    if call.data == "next_image":
        # Получаем текущий баланс
        balance = get_user_balance(user_id)

        # Проверяем, достаточно ли монет для получения новой картинки
        if balance >= 2:
            update_user_balance(user_id, -2)  # Снимаем 2 монеты
            get_image(call.message)  # Вызываем функцию для получения картинки
        else:
            bot.send_message(call.message.chat.id, f"""Бесплатные шуточки про мамашу закончились, 
каждые 2 часа возобновляеться 1 монетка! 
Стоимость 1 картинки - 2 монетки
Ваш баланс: {balance} монеток💰""")
# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(message.chat.id, open('welcomePhoto.jfif', 'rb'), caption="""Оу да, Маквин готов!🚘
Хочешь получить шуточки про мамашу пиши - /get_image 🌼 
Посмотреть баланс монеток - /balance 💸


➡️Хотите своего телграмм/дискорд бота? - @zefruuu
➡️Недорогая реклама - @zefruuu """, reply_markup=markup)
    
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
/help - все команды▶️

➡️Хотите своего телграмм/дискорд бота? - @zefruuu
➡️Недорогая реклама - @zefruuu
"""
            )

#клавіатура
markup = ReplyKeyboardMarkup(resize_keyboard=True)
item1 = KeyboardButton("/balance 👛")
item2 = KeyboardButton("/start 🔄")
item3 = KeyboardButton("/help 🆘")
item4 = KeyboardButton("/get_image 🖼")
markup.add(item1, item2)
markup.add(item3, item4)
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



import sqlite3
from telebot import TeleBot
from Tokens import admin_tok

TOKEN = admin_tok.key
PASSWORD = '0921'  # set your password here

bot = TeleBot(TOKEN)
#
conn = sqlite3.connect('image_database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        image BLOB,
        user_id INTEGER
    )
''')
conn.commit()
conn.close()

conn = sqlite3.connect('image_database.db')
cursor = conn.cursor()
cursor.execute('''
    PRAGMA table_info(images)
''')
columns = [tup[1] for tup in cursor.fetchall()]
if 'user_id' not in columns:
    cursor.execute('''
        ALTER TABLE images ADD COLUMN user_id INTEGER
    ''')
conn.commit()
conn.close()

users = {}  # store users who have entered the password

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in users:
        bot.send_message(message.chat.id, 'Enter the password to access the bot')
        bot.register_next_step_handler(message, check_password)
    else:
        help(message)

def check_password(message):
    if message.text == PASSWORD:
        users[message.from_user.id] = True
        help(message)
    else:
        bot.send_message(message.chat.id, 'Invalid password')

@bot.message_handler(commands=['help'])
def help(message):
    if message.from_user.id in users:
        bot.send_message(message.chat.id, '''
Available commands:

/addPhoto - Add a photo to the database
/stats - Show the total number of images uploaded
/deletePhoto - Delete a photo by ID
/deleteAllPhotos - Delete all photos in the database
/showPhoto - Show a photo by ID
/help - Show this help message
''')
    else:
        bot.send_message(message.chat.id, 'You need to enter the password first')

@bot.message_handler(commands=['addPhoto'])
def add_photo(message):
    if message.from_user.id in users:
        bot.send_message(message.chat.id, 'Send a photo to add to the database')
        bot.register_next_step_handler(message, process_photo)
    else:
        bot.send_message(message.chat.id, 'You need to enter the password first')

def process_photo(message):
    if message.content_type == 'photo':
        image = bot.get_file(message.photo[-1].file_id)
        image_bytes = bot.download_file(image.file_path)
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO images (image, user_id) VALUES (?, ?)', (image_bytes, message.from_user.id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f'Image added to the database with ID {cursor.lastrowid}')
    else:
        bot.send_message(message.chat.id, 'Please send a photo')

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id in users:
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        total_images = cursor.fetchone()[0]
        conn.close()
        bot.send_message(message.chat.id, f'Total images uploaded: {total_images}')
    else:
        bot.send_message(message.chat.id, 'You need to enter the password first')

@bot.message_handler(commands=['deletePhoto'])
def delete_photo(message):
    if message.from_user.id in users:
        bot.send_message(message.chat.id, 'Send the ID of the photo to update')
        bot.register_next_step_handler(message, process_update_photo)
    else:
        bot.send_message(message.chat.id, 'You need to enter the password first')

def process_update_photo(message):
    try:
        photo_id = int(message.text)
        bot.send_message(message.chat.id, 'Send the new photo to update')
        bot.register_next_step_handler(message, process_update_photo_with_image, photo_id)
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid ID')

def process_update_photo_with_image(message, photo_id):
    if message.content_type == 'photo':
        image = bot.get_file(message.photo[-1].file_id)
        image_bytes = bot.download_file(image.file_path)
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE images SET image = ? WHERE id = ?', (image_bytes, photo_id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f'Photo with ID {photo_id} updated successfully')
    else:
        bot.send_message(message.chat.id, 'Please send a photo')

@bot.message_handler(commands=['deleteAllPhotos'])
def delete_all_photos(message):
    if message.from_user.id in users:
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM images')
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, 'All photos deleted')
    else:
        bot.send_message(message.chat.id, 'You need to enter the password first')

@bot.message_handler(commands=['showPhoto'])
@bot.message_handler(commands=['showPhoto'])
def show_photo(message):
    if message.from_user.id in users:
        bot.send_message(message.chat.id, 'Send the ID of the photo to show')
        bot.register_next_step_handler(message, process_show_photo)
    else:
        bot.send_message(message.chat.id, 'You need to enter the password first')

def process_show_photo(message):
    try:
        photo_id = int(message.text)
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT image FROM images WHERE id = ?', (photo_id,))
        image_bytes = cursor.fetchone()[0]
        bot.send_photo(message.chat.id, image_bytes)
        conn.close()
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid ID')
    except TypeError:
        bot.send_message(message.chat.id, 'Photo not found')

bot.infinity_polling()
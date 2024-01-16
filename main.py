import telebot # импорт библиотеки для Telegram-ботов
import sqlite3 # Импорт базы данных
import datetime

import extension as e # импорт файла 'extension.py' с классами ошибок

from telebot import types
from config import TOKEN # импорт токена из файла 'config.py'

bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

# Проверяем создана ли таблица, если нет - создаем
with conn: 
    data = conn.execute("select count(*) from sqlite_master where type='table' and name='tasks'") 
    for row in data: 
        if row[0] == 0: 
            with conn: 
                conn.execute(""" CREATE TABLE tasks ( userid VARCHAR(40), time VARCHAR(20), task_headline VARCHAR(100), task_text VARCHAR(500) ); """)

@bot.message_handler(commands= ['start']) # функция ответа на сообщения /start
def start(message: telebot.types.Message):
    text = f'Привет {message.from_user.first_name}! \n\
Я - чат-бот помощник, который запишет все твои дела, которые ты мне отправишь.\n\
Если не знаешь с чего начать, то воспользуйся командой /help чтобы посмотреть все доступные команды.'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Поздороваться')
    btn2 = types.KeyboardButton('Создать задачу')
    btn3 = types.KeyboardButton('Посмотреть задачи')
    btn4 = types.KeyboardButton('Помощь')
    markup.add(btn1, btn2, btn3, btn4)
    bot.reply_to(message, text, reply_markup=markup)

@bot.message_handler(commands= ['add_task']) # команда добавления задачи в базу данных
def add_task(message: telebot.types.Message):
    text = 'Добавление задачи в список дел.\n\
Введите время, когда нужно приступить к выполнению задачи.\n\
Например: 14:30.'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, add_task_time)

def add_task_time(message: telebot.types.Message):
    user_time = message.text
    # Проверяем корректность пользовательского ввода времени
    try:
        time_obj = datetime.datetime.strptime(user_time, '%H:%M')
        time = time_obj.time().strftime('%H:%M')
        conn = sqlite3.connect('db/database.db') # подключаемся к базе 
        sql = 'INSERT INTO tasks (userid, time, task_headline, task_text) values(?, ?, ?, ?)' # подготавливаем запрос 
        data = [ (str(message.from_user.id), str(time), str('.'), str('.')) ] # формируем данные для запроса 
        # добавляем с помощью запроса данные 
        with conn: 
            conn.executemany(sql, data) 
        text = f'Отлично, время {time}, дальше введите заголовок задачи.'
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, add_task_headline)
    # Если время не соответсвует формату ЧЧ:ММ - выводим сообщение с ошибкой
    except:
        text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 09:35')
        bot.register_next_step_handler(text, add_task_time)

def add_task_headline(message: telebot.types.Message):
    headline = str(message.text)
    text = f'Хорошо, заголовок "{headline}", теперь введите описание задачи.'
    conn = sqlite3.connect('db/database.db')
    with conn:
        data = conn.execute(f'SELECT * FROM tasks WHERE userid LIKE {message.from_user.id}')
        for row in data:
            if row[:-1]:
                conn.execute(f'UPDATE tasks SET task_headline = REPLACE(task_headline, ".", "{headline}")')
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, add_task_descr)

def add_task_descr(message: telebot.types.Message):
    descr = message.text
    text = 'Отлично, задача создана!'
    conn = sqlite3.connect('db/database.db')
    with conn:
        data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id}')
        for row in data:
            if row[:-1]:
                conn.execute(f'UPDATE tasks SET task_text = REPLACE(task_text, ".", "{descr}")')
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['show_tasks']) # Команда просмотра списка задач
def show_tasks(message: telebot.types.Message):
    text = 'Вот все твои актуальные задачи:'
    bot.send_message(message.chat.id, text)
    conn = sqlite3.connect('db/database.db')
    all_tasks = '.'
    with conn:
        data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} ORDER BY time')
        count = 1
        for row in data:
            all_tasks = f'*Задача №{count}*' + '\n' + f'*Время: {row[1]}* ' + '\n' + f'Заголовок: {row[2]}' + '\n' + f'Описание: {row[3]}' + '\n\n'
            count += 1
            markup = types.InlineKeyboardMarkup()
            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
            markup.add(btn_edit, btn_complete)
            bot.send_message(message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
            all_tasks = ''
        if all_tasks == '.':
            all_tasks = 'У тебя нет актуальных задач. Чтобы создать новую нажми "Создать задачу"'
            bot.send_message(message.chat.id, all_tasks)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'complete': # Выполнение задачи и удаление из базы данных
            task_time = call.message.text.split(" ")[2]
            with conn:
                data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id}')
                for row in data:
                    if row[1] == task_time:
                        conn.execute(f'DELETE FROM tasks WHERE time = "{task_time}"')
                        break
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text='Задача выполнена и удалена из списка.')
        elif call.data == 'edit': # Редактирует задачу
            markup = types.InlineKeyboardMarkup()
            btn_time = types.InlineKeyboardButton('Время', callback_data='time')
            btn_headline = types.InlineKeyboardButton('Заголовок', callback_data='headline')
            btn_descr = types.InlineKeyboardButton('Описание', callback_data='descr')
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back')
            markup.add(btn_time, btn_headline, btn_descr, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        # Callback функции для редактирования задачи
        elif call.data == 'time': # Изменение времени задачи
            bot.delete_message(call.message.chat.id, call.message.message_id)
            msg = bot.send_message(call.message.chat.id, text='Введите новое время в чат.')
            bot.register_next_step_handler(msg, edit_time)
            global old_time
            old_time = call.message.text.split(" ")[2]
        elif call.data == 'headline':
            bot.send_message(call.message.chat.id, text='В разработке')
        elif call.data == 'descr':
            bot.send_message(call.message.chat.id, text='В разработке')
        elif call.data == 'back':
            markup = types.InlineKeyboardMarkup()
            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
            markup.add(btn_edit, btn_complete)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
            
def edit_time(message: telebot.types.Message):
    new_user_time = message.text
    try: 
        time_obj = datetime.datetime.strptime(new_user_time, '%H:%M')
        new_time = time_obj.time().strftime('%H:%M')
        with conn:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id}')
            for row in data:
                if row[1] == old_time:
                    conn.execute(f'UPDATE tasks SET time = REPLACE(time, "{old_time}", "{new_time}")')
        text = 'Время успешно изменено.'
        bot.send_message(message.chat.id, text)
    except:
        text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 09:35')
        bot.register_next_step_handler(text, edit_time)

@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    if message.text == '/help' or 'Помощь':
        text = 'Глянь, вот команды для меня, которые ты можешь использовать и их краткое описание:\n\
/start - начать использование.\n\
/help - посмотреть список всех команд.\n\
/add_task - добавить задачу.\n\
/show_tasks - посмотреть список задач.'
        bot.reply_to(message, text)

@bot.message_handler(content_types=['text'])
def task_text(message: telebot.types.Message):
    if message.text == 'Поздороваться':
        text = 'Привет-привет. Какие дела добавить в список сегодня?'
        bot.reply_to(message, text)
    elif message.text == 'Помощь':
        help(message)
    elif message.text == 'Создать задачу':
        add_task(message)
    elif message.text == 'Посмотреть задачи':
        show_tasks(message)
    else:
        split_text = message.text.split()
        user_id = message.from_user.id
        text = 'Прости, я еще не научился вести диалог, но, возможно, и это я смогу делать :)'
        bot.reply_to(message, text)
        
if __name__ == '__main__':
    bot.infinity_polling()

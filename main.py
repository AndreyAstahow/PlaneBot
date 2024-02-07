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
    btn1 = types.KeyboardButton('Создать задачу')
    btn2 = types.KeyboardButton('Посмотреть задачи')
    btn3 = types.KeyboardButton('Помощь')
    markup.add(btn1, btn2, btn3)
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
        # Проверяем верно ли указано время после ':'
        if len(user_time.split(':')[1]) < 2:
            text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 9:35')
            bot.register_next_step_handler(text, add_task_time)
        else:
            time_obj = datetime.datetime.strptime(user_time, '%H:%M')
            time = time_obj.time().strftime('%H:%M')
            # добавляем с помощью запроса данные 
            with conn:
                data_time = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND time = "{time}"')
                fetch = data_time.fetchall()
                if len(fetch) > 0:
                    text = 'Это время уже занято, выберите другое.'
                    msg = bot.send_message(message.chat.id, text)
                    bot.register_next_step_handler(msg, add_task_time)
                else:
                    sql = 'INSERT INTO tasks (userid, time, task_headline, task_text) values(?, ?, ?, ?)' # подготавливаем запрос 
                    data = [ (str(message.from_user.id), str(time), str('.'), str('.')) ] # формируем данные для запроса 
                    conn.executemany(sql, data)
                    text = 'Введите заголовок задачи.'
                    msg = bot.send_message(message.chat.id, text)
                    bot.register_next_step_handler(msg, add_task_headline)
    except IndexError:
            text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 9:35')
            bot.register_next_step_handler(text, add_task_time)
# Если время не соответсвует формату ЧЧ:ММ - выводим сообщение с ошибкой
    except:
        text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 9:35')
        bot.register_next_step_handler(text, add_task_time)
        # bot.send_message(message.chat.id, text=time)

def add_task_headline(message: telebot.types.Message):
    headline = message.text
    with conn:
        data_headline = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_headline = "{headline}"')
        fetch = data_headline.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким заголовком уже есть. Выберите другой.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, add_task_headline)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid LIKE {message.from_user.id}')
            for row in data:
                if row[:-1]:
                    conn.execute(f'UPDATE tasks SET task_headline = REPLACE(task_headline, ".", "{headline}")')
            text = 'Введите описание задачи.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, add_task_descr)

def add_task_descr(message: telebot.types.Message):
    descr = message.text
    with conn:
        data_descr = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_text = "{descr}"')
        fetch = data_descr.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким описанием уже есть. Выберите другое.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, add_task_descr)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id}')
            for row in data:
                if row[:-1]:
                    conn.execute(f'UPDATE tasks SET task_text = REPLACE(task_text, ".", "{descr}")')
            text = 'Отлично, задача создана!'
            bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['show_tasks']) # Команда просмотра списка задач
def show_tasks(message: telebot.types.Message):
    text = 'Вот все твои актуальные задачи:'
    bot.send_message(message.chat.id, text)
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
            bot.delete_message(call.message.chat.id, call.message.message_id)
            msg = bot.send_message(call.message.chat.id, text='Введите новый заголовок в чат.')
            bot.register_next_step_handler(msg, edit_headline)
            old_headline_ = call.message.text.split('\n')[2]
            global old_headline
            old_headline = old_headline_.split('Заголовок: ')[1]
        elif call.data == 'descr':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            msg = bot.send_message(call.message.chat.id, text='Введите новое описание в чат.')
            bot.register_next_step_handler(msg, edit_descr)
            old_descr_ = call.message.text.split('\n')[3]
            global old_descr
            old_descr = old_descr_.split('Описание: ')[1]
        elif call.data == 'back':
            markup = types.InlineKeyboardMarkup()
            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
            markup.add(btn_edit, btn_complete)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
            
# Функция редактирования времени
def edit_time(message: telebot.types.Message):
    new_user_time = message.text
    try: 
        if len(new_user_time.split(':')[1]) < 2:
            text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 9:35')
            bot.register_next_step_handler(text, edit_time)
        else:
            time_obj = datetime.datetime.strptime(new_user_time, '%H:%M')
            new_time = time_obj.time().strftime('%H:%M')
            with conn:
                data_time = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND time = "{new_time}"')
                fetch = data_time.fetchall()
                if len(fetch) > 0:
                    text = 'Это время уже занято, выберите другое.'
                    msg = bot.send_message(message.chat.id, text)
                    bot.register_next_step_handler(msg, edit_time)
                else:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id}')
                    for row in data:
                        if row[1] == old_time:
                            conn.execute(f'UPDATE tasks SET time = REPLACE(time, "{old_time}", "{new_time}")')
                            text = 'Время успешно изменено.'
                            bot.send_message(message.chat.id, text)
    except IndexError:
        text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 9:35')
        bot.register_next_step_handler(text, edit_time)
    except:
        text = bot.send_message(message.chat.id, text='Введите корректное время в формате ЧЧ:ММ.\n\
Например: 09:35')
        bot.register_next_step_handler(text, edit_time)

# Функция редактирования заголовка
def edit_headline(message: telebot.types.Message):
    new_headline = message.text
    with conn:
        data_headline = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_headline = "{new_headline}"')
        fetch = data_headline.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким заголовком уже есть. Выберите другой.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, edit_headline)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id}')
            for row in data:
                if row[2] == old_headline:
                    conn.execute(f'UPDATE tasks SET task_headline = REPLACE(task_headline, "{old_headline}", "{new_headline}")')
            text = 'Заголовок успешно изменен.'
            bot.send_message(message.chat.id, text)

def edit_descr(message: telebot.types.Message):
    new_descr = message.text
    with conn:
        data_descr = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_headline = "{new_descr}"')
        fetch = data_descr.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким описанием уже есть. Выберите другое.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, edit_descr)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id}')
            for row in data:
                if row[3] == old_descr:
                    conn.execute(f'UPDATE tasks SET task_text = REPLACE(task_text, "{old_descr}", "{new_descr}")')
            text = 'Описание успешно изменено.'
            bot.send_message(message.chat.id, text)

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
    if message.text.lower() == 'помощь':
        help(message)
    elif message.text.lower() == 'создать задачу':
        add_task(message)
    elif message.text.lower() == 'посмотреть задачи':
        show_tasks(message)
    elif message.text.lower() == 'назад'.lower():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Создать задачу')
        btn2 = types.KeyboardButton('Посмотреть задачи')
        btn3 = types.KeyboardButton('Помощь')
        markup.add(btn1, btn2, btn3)
        bot.reply_to(message, text='Главное меню', reply_markup=markup)
    elif message.text.lower() == '/calendar':
        calendar(message)
    else:
        text = 'Прости, я еще не научился вести диалог, но, возможно, и это я смогу делать :)'
        bot.reply_to(message, text)

@bot.message_handler(commands=['calendar'])
def calendar(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    january = types.KeyboardButton('Январь')
    back = types.KeyboardButton('Назад')
    markup.add(january, back)
    bot.send_message(message.chat.id, text='Выберите дату', reply_markup=markup)


if __name__ == '__main__':
    # bot.polling(non_stop=True)
    bot.infinity_polling()

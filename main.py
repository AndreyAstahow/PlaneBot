import telebot # импорт библиотеки для Telegram-ботов
import sqlite3 # Импорт базы данных
import datetime
import calendar as cal

# import schedule
from threading import Thread
from time import sleep

from telebot import types
from config import TOKEN, months # импорт токена из файла 'config.py'

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
                conn.execute(""" CREATE TABLE tasks ( userid VARCHAR(40), task_date VARCHAR(20), time VARCHAR(20), task_headline VARCHAR(100), task_text VARCHAR(500) ); """)

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
    global user_chat_id, user_id
    user_chat_id = message.chat.id
    user_id = message.from_user.id
    # schedule.clear()
    # start_checker()

@bot.message_handler(commands= ['add_task']) # команда добавления задачи в базу данных
def add_task(message: telebot.types.Message):
    text = 'Добавление задачи в список дел.'
    bot.send_message(message.chat.id, text)
    add_task_date(message)

def add_task_date(message: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_january = telebot.types.InlineKeyboardButton('Январь', callback_data='january')
    btn_fabruary = telebot.types.InlineKeyboardButton('Февраль', callback_data='fabruary')
    btn_march = telebot.types.InlineKeyboardButton('Март', callback_data='march')
    btn_april = telebot.types.InlineKeyboardButton('Апрель', callback_data='april')
    btn_may = telebot.types.InlineKeyboardButton('Май', callback_data='may')
    btn_june = telebot.types.InlineKeyboardButton('Июнь', callback_data='june')
    btn_july = telebot.types.InlineKeyboardButton('Июль', callback_data='july')
    btn_august = telebot.types.InlineKeyboardButton('Август', callback_data='august')
    btn_september = telebot.types.InlineKeyboardButton('Сентябрь', callback_data='september')
    btn_october = telebot.types.InlineKeyboardButton('Октябрь', callback_data='october')
    btn_november = telebot.types.InlineKeyboardButton('Ноябрь', callback_data='november')
    btn_december = telebot.types.InlineKeyboardButton('Декабрь', callback_data='december')
    all_btn_months = [btn_january, btn_fabruary, btn_march, btn_april, btn_may, btn_june, btn_july, btn_august, btn_september, btn_october, btn_november, btn_december]
    month_now = datetime.datetime.now().month
    for i in range(1, 12):
        if month_now == i:
            for n in range(i, 12):
                markup.add(*all_btn_months[n-1:])
                break
            break
    text = 'Выберите дату:'
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)     

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
                data_time = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND time = "{time}" AND task_date ="{date}"')
                fetch = data_time.fetchall()
                if len(fetch) > 0:
                    text = 'Это время уже занято, выберите другое.'
                    msg = bot.send_message(message.chat.id, text)
                    bot.register_next_step_handler(msg, add_task_time)
                else:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid LIKE {message.from_user.id}')
                    for row in data:
                        if row[:-1]:
                            conn.execute(f'UPDATE tasks SET time = REPLACE(time, ".", "{time}")')
                            text = 'Введите заголовок задачи.'
                            msg = bot.send_message(message.chat.id, text)
                            bot.register_next_step_handler(msg, add_task_headline)
                            break
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
        data_headline = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_headline = "{headline}" AND task_date = "{date}"')
        fetch = data_headline.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким заголовком уже есть. Выберите другой.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, add_task_headline)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{date}"')
            for row in data:
                if row[:-1]:
                    conn.execute(f'UPDATE tasks SET task_headline = REPLACE(task_headline, ".", "{headline}")')
            text = 'Введите описание задачи.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, add_task_descr)

def add_task_descr(message: telebot.types.Message):
    descr = message.text
    with conn:
        data_descr = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_text = "{descr}" AND task_date = "{date}"')
        fetch = data_descr.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким описанием уже есть. Выберите другое.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, add_task_descr)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{date}"')
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
        data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} ORDER BY task_date, time')
        count = 1
        for row in data:
            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
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

@bot.message_handler(commands=['show_task_today'])
def show_task_today(message: telebot.types.Message):
    text = 'Вот все твои задачи на сегодня:'
    bot.send_message(message.chat.id, text)
    today = f"{datetime.datetime.now().day} {months[datetime.datetime.now().month]}"
    all_tasks = '.'
    with conn:
        data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{today}" ORDER BY task_date, time')
        count = 1
        for row in data:
            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
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

@bot.message_handler(commands=['show_task_tommorow'])
def show_task_tommorow(message: telebot.types.Message):
    day = datetime.datetime.now().day + 1
    month = datetime.datetime.now().month
    tommorow = f'{day} {months[month]}'
    max_days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
    if day > max_days:
        day = 1
        month += 1
        if month > 12:
            month = 1
            tommorow = f'{day} {months[month]}'
        else:
            tommorow = f'{day} {months[month]}'
    else:
        tommorow = f'{day} {months[month]}'

    text = f'Вот все твои задачи на завтра, {tommorow}:'
    bot.send_message(message.chat.id, text)

    with conn:
        all_tasks = '.'
        data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{tommorow}" ORDER BY time')
        count = 1
        for row in data:
            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
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


@bot.message_handler(commands=['show_task_week'])
def show_task_week(message: telebot.types.Message):
    day_list = []
    today = datetime.datetime.now().day
    month = datetime.datetime.now().month
    max_days_month = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
    for i in range(7):
        if today > max_days_month:
            today = 1
            month += 1
            if month > 12:
                month = 1
                day = f'{today} {months[month]}'
                day_list.append(day)
                today += 1
            else:
                day = f'{today} {months[month]}'
                day_list.append(day)
                today += 1
        else:
            day = f'{today} {months[month]}'
            day_list.append(day)
            today += 1
    text = f'Вот все ваши задачи с {day_list[0]} по {day_list[-1]}:'
    bot.send_message(message.chat.id, text)
    task_list = []
    with conn:
        for i in day_list:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{i}" ORDER BY time')
            count = 1
            all_tasks = '.'
            for row in data:
                if row:
                    text = f'Задачи на {i}.'
                    bot.send_message(message.chat.id, text)
                    all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                    task_list.append(all_tasks)
                    count += 1
                    markup = types.InlineKeyboardMarkup()
                    btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                    btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                    markup.add(btn_edit, btn_complete)
                    bot.send_message(message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                    all_tasks = ''
            if all_tasks == '.':
                continue
    if len(task_list) < 1:
        text = f'C {day_list[0]} по {day_list[-1]} задач нет. Чтобы создать задачу нажми "Создать задачу"'
        bot.send_message(message.chat.id, text)

@bot.message_handler(command=['show_task_selected_day'])
def show_task_selected_day(message: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_january = telebot.types.InlineKeyboardButton('Январь', callback_data='january_show')
    btn_fabruary = telebot.types.InlineKeyboardButton('Февраль', callback_data='fabruary_show')
    btn_march = telebot.types.InlineKeyboardButton('Март', callback_data='march_show')
    btn_april = telebot.types.InlineKeyboardButton('Апрель', callback_data='april_show')
    btn_may = telebot.types.InlineKeyboardButton('Май', callback_data='may_show')
    btn_june = telebot.types.InlineKeyboardButton('Июнь', callback_data='june_show')
    btn_july = telebot.types.InlineKeyboardButton('Июль', callback_data='july_show')
    btn_august = telebot.types.InlineKeyboardButton('Август', callback_data='august_show')
    btn_september = telebot.types.InlineKeyboardButton('Сентябрь', callback_data='september_show')
    btn_october = telebot.types.InlineKeyboardButton('Октябрь', callback_data='october_show')
    btn_november = telebot.types.InlineKeyboardButton('Ноябрь', callback_data='november_show')
    btn_december = telebot.types.InlineKeyboardButton('Декабрь', callback_data='december_show')
    all_btn_months = [btn_january, btn_fabruary, btn_march, btn_april, btn_may, btn_june, btn_july, btn_august, btn_september, btn_october, btn_november, btn_december]
    month_now = datetime.datetime.now().month
    for i in range(1, 12):
        if month_now == i:
            for n in range(i, 12):
                markup.add(*all_btn_months[n-1:])
                break
            break
    text = 'Выберите дату:'
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup) 

@bot.callback_query_handler(func=lambda call: True)
def callback_msg_button(call):
    if call.message:
        if call.data == 'complete': # Выполнение задачи и удаление из базы данных
            task_time = call.message.text.split(" ")[8]
            task_date = f'{call.message.text.split(" ")[5]} {call.message.text.split(" ")[6]}'
            with conn:
                data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id}')
                for row in data:
                    if row[2] == task_time and row[1] == task_date:
                        conn.execute(f'DELETE FROM tasks WHERE time = "{task_time}" AND task_date = "{task_date}"')
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
            global old_time
            old_time = call.message.text.split(" ")[8]
            msg = bot.send_message(call.message.chat.id, text='Введите новое время в чат.')
            bot.register_next_step_handler(msg, edit_time)
        elif call.data == 'headline':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            old_headline_ = call.message.text.split('\n')[2]
            global old_headline, old_task_date
            old_task_date = f'{call.message.text.split(" ")[5]} {call.message.text.split(" ")[6]}'
            bot.send_message(call.message.chat.id, old_task_date)
            old_headline = old_headline_.split('Заголовок: ')[1]
            msg = bot.send_message(call.message.chat.id, text='Введите новый заголовок в чат.')
            bot.register_next_step_handler(msg, edit_headline)
        elif call.data == 'descr':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            old_descr_ = call.message.text.split('\n')[3]
            global old_descr, old_task_date_2
            old_task_date_2 = f'{call.message.text.split(" ")[5]} {call.message.text.split(" ")[6]}'
            old_descr = old_descr_.split('Описание: ')[1]
            msg = bot.send_message(call.message.chat.id, text='Введите новое описание в чат.')
            bot.register_next_step_handler(msg, edit_descr)
        elif call.data == 'back':
            markup = types.InlineKeyboardMarkup()
            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
            markup.add(btn_edit, btn_complete)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        

        elif call.data == 'back_montn':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            add_task_date(call.message)
        elif call.data == 'january':
            markup = types.InlineKeyboardMarkup()
            month = 1
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'junary {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'junary {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'fabruary':
            markup = types.InlineKeyboardMarkup()
            month = 2
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'fabruary {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'fabruary {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'march':
            markup = types.InlineKeyboardMarkup()
            month = 3
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'march {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'march {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'april':
            markup = types.InlineKeyboardMarkup()
            month = 4
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'april {i}')
                        btn.append(btn_date)
                    else:
                        continue        
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'april {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'may':
            markup = types.InlineKeyboardMarkup()
            month = 5
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'may {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'may {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'june':
            markup = types.InlineKeyboardMarkup()
            month = 6
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'june {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'june {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'july':
            markup = types.InlineKeyboardMarkup()
            month = 7
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'july {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'july {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'august':
            markup = types.InlineKeyboardMarkup()
            month = 8
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'august {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'august {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'september':
            markup = types.InlineKeyboardMarkup()
            month = 9
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'september {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'september {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'october':
            markup = types.InlineKeyboardMarkup()
            month = 10
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'october {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'october {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'november':
            markup = types.InlineKeyboardMarkup()
            month = 11
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'november {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'november {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'december':
            markup = types.InlineKeyboardMarkup()
            month = 12
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'december {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'december {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        
        # callback-функции для @show_task_selected_day
        elif call.data == 'january_show':
            markup = types.InlineKeyboardMarkup()
            month = 1
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_january {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_january {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'fabruary_show':
            markup = types.InlineKeyboardMarkup()
            month = 2
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_fabruary {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_fabruary {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'march_show':
            markup = types.InlineKeyboardMarkup()
            month = 3
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_march {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_march {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'april_show':
            markup = types.InlineKeyboardMarkup()
            month = 4
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_april {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_april {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'may_show':
            markup = types.InlineKeyboardMarkup()
            month = 5
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_may {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_may {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'june_show':
            markup = types.InlineKeyboardMarkup()
            month = 6
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_june {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_june {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'july_show':
            markup = types.InlineKeyboardMarkup()
            month = 7
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_july {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_july {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'august_show':
            markup = types.InlineKeyboardMarkup()
            month = 8
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_august {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_august {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'september_show':
            markup = types.InlineKeyboardMarkup()
            month = 9
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_september {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_september {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'october_show':
            markup = types.InlineKeyboardMarkup()
            month = 10
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_october {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_october {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'november_show':
            markup = types.InlineKeyboardMarkup()
            month = 11
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_november {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_november {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)
        elif call.data == 'december_show':
            markup = types.InlineKeyboardMarkup()
            month = 12
            days = cal.monthrange(year=datetime.datetime.now().year, month=month)[1]
            numbers = list(range(1, days+1))
            btn = []
            for i in numbers:
                if datetime.datetime.now().month == month:
                    if i >= datetime.datetime.now().day:
                        btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_december {i}')
                        btn.append(btn_date)
                else:
                    btn_date = types.InlineKeyboardButton(f'{i}', callback_data=f'show_december {i}')
                    btn.append(btn_date)
            btn_back = types.InlineKeyboardButton('Назад', callback_data='back_montn')
            markup.add(*btn, btn_back)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)

        numbers = list(range(1, 32))
        for i in numbers:
            global date
            if call.data == f'january {i}':
                date = f"{i} января"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} января'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} января.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'fabruary {i}':
                date = f"{i} февраля"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} февраля'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} февраля.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'march {i}':
                date = f"{i} марта"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} марта'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} марта.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'april {i}':
                bot.send_message(call.message.chat.id, text=f"Выбрана дата: {i} апреля")
                date = f"{i} апреля"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} апреля'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} апреля.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'may {i}':
                date = f"{i} мая"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} мая'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} мая.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'june {i}':
                date = f"{i} июня"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} июня'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} июня.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'july {i}':
                date = f"{i} июля"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} июля'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} июля.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'august {i}':
                date = f"{i} августа"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} августа'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} августа.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'september {i}':
                date = f"{i} сентября"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} сентября'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} сентября.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'october {i}':
                date = f"{i} октября"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} октября'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} октября.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'november {i}':
                date = f"{i} ноября"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} ноября'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} ноября.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)
            elif call.data == f'december {i}':
                date = f"{i} декабря"
                with conn:
                    sql = 'INSERT INTO tasks (userid, task_date, time, task_headline, task_text) values(?, ?, ?, ?, ?)'
                    data = [ (str(call.from_user.id), str(f'{i} декабря'), str('.'), str('.'), str('.')) ]
                    conn.executemany(sql, data)
                text = f'Выбрана дата: {i} декабря.\n\
Введите время для выполнения задачи задачи в формате ЧЧ:ММ.\n\
Например: 9:30'
                msg = bot.send_message(call.message.chat.id, text)
                bot.register_next_step_handler(msg, add_task_time)


            elif call.data == f'show_january {i}':
                text = f'Вот все твои задачи на {i} января:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} января" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} января нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_february {i}':
                text = f'Вот все твои задачи на {i} февраля:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} февраля" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} февраля нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_march {i}':
                text = f'Вот все твои задачи на {i} марта:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} марта" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} марта нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_april {i}':
                text = f'Вот все твои задачи на {i} апреля:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} апреля" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} апреля нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_may {i}':
                text = f'Вот все твои задачи на {i} мая:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} мая" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} мая нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_june {i}':
                text = f'Вот все твои задачи на {i} июня:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} июня" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} июня нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_july {i}':
                text = f'Вот все твои задачи на {i} июля:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} июля" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} июля нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_august {i}':
                text = f'Вот все твои задачи на {i} августа:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} августа" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} августа нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_september {i}':
                text = f'Вот все твои задачи на {i} сентября:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} сентября" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} сентября нет. Чтобы создать новую задачу выберите "Создать задачу" '
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_october {i}':
                text = f'Вот все твои задачи на {i} октября:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} октября" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} октября нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_november {i}':
                text = f'Вот все твои задачи на {i} ноября:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} ноября" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} ноября нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
            elif call.data == f'show_december {i}':
                text = f'Вот все твои задачи на {i} декабря:'
                bot.send_message(call.message.chat.id, text)
                with conn:
                    data = conn.execute(f'SELECT * FROM tasks WHERE userid = {call.from_user.id} AND task_date = "{i} декабря" ORDER BY time')
                    count = 1
                    all_tasks = '.'
                    for row in data:
                        if row:
                            all_tasks = f'*Задача №{count}* ' + '\n' + f'*Дата и время: {row[1]} в {row[2]}* ' + '\n' + f'Заголовок: {row[3]}' + '\n' + f'Описание: {row[4]}' + '\n\n'
                            count += 1
                            markup = types.InlineKeyboardMarkup()
                            btn_edit = types.InlineKeyboardButton('Редактировать✏️', callback_data = 'edit')
                            btn_complete = types.InlineKeyboardButton("Выполнено✅", callback_data = 'complete')
                            markup.add(btn_edit, btn_complete)
                            bot.send_message(call.message.chat.id, all_tasks, parse_mode='Markdown', reply_markup=markup)
                            all_tasks = ''
                    if all_tasks == '.':
                        text = f'Задач на {i} декабря нет. Чтобы создать новую задачу выберите "Создать задачу"'
                        bot.send_message(call.message.chat.id, text)
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
                        if row[2] == old_time:
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
        data_headline = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_headline = "{new_headline}" AND task_date = "{old_task_date}"')
        fetch = data_headline.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким заголовком уже есть. Выберите другой.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, edit_headline)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{old_task_date}"')
            for row in data:
                if row[3] == old_headline:
                    conn.execute(f'UPDATE tasks SET task_headline = REPLACE(task_headline, "{old_headline}", "{new_headline}") WHERE task_date = "{old_task_date}"')
            text = 'Заголовок успешно изменен.'
            bot.send_message(message.chat.id, text)

def edit_descr(message: telebot.types.Message):
    new_descr = message.text
    with conn:
        data_descr = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_headline = "{new_descr}" AND task_date = "{old_task_date_2}"')
        fetch = data_descr.fetchall()
        if len(fetch) > 0:
            text = 'Задача с таким описанием уже есть. Выберите другое.'
            msg = bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(msg, edit_descr)
        else:
            data = conn.execute(f'SELECT * FROM tasks WHERE userid = {message.from_user.id} AND task_date = "{old_task_date_2}"')
            for row in data:
                if row[4] == old_descr:
                    conn.execute(f'UPDATE tasks SET task_text = REPLACE(task_text, "{old_descr}", "{new_descr}") WHERE task_date = "{old_task_date_2}"')
            text = 'Описание успешно изменено.'
            bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    if message.text == '/help' or 'Помощь':
        text = 'Глянь, вот команды для меня, которые ты можешь использовать и их краткое описание:\n\
/start - начать использование.\n\
/help - посмотреть список всех команд.\n\
/add_task - добавить задачу.\n\
/show_tasks - посмотреть список задач.\n\
/show_task_today - посмотреть задачи на сегодня.\n\
/show_task_tommorow - посмотреть задачи на завтра.\n\
/show_task_week - посмореть задачи на неделю.\n\
/show_task_selected_day - посмотреть задачи на определенный день.'
        bot.reply_to(message, text)

@bot.message_handler(content_types=['text'])
def task_text(message: telebot.types.Message):
    if message.text.lower() == 'помощь':
        help(message)
    elif message.text.lower() == 'создать задачу':
        add_task(message)
    elif message.text.lower() == 'посмотреть задачи':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_today = types.KeyboardButton('Сегодня')
        btn_tommorow = types.KeyboardButton('Завтра')
        btn_week = types.KeyboardButton('Неделю')
        btn_person_day = types.KeyboardButton('На другой день')
        btn_back = types.KeyboardButton('Назад')
        markup.add(btn_today, btn_tommorow, btn_week, btn_person_day, btn_back)
        bot.send_message(message.chat.id, text='На какой день проверить задачи?', reply_markup=markup)
    elif message.text.lower() == 'сегодня':
        show_task_today(message)
    elif message.text.lower() == 'завтра':
        show_task_tommorow(message)
    elif message.text.lower() == 'неделю':
        show_task_week(message)
    elif message.text.lower() == 'на другой день':
        show_task_selected_day(message)
    elif message.text.lower() == 'назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Создать задачу')
        btn2 = types.KeyboardButton('Посмотреть задачи')
        btn3 = types.KeyboardButton('Помощь')
        markup.add(btn1, btn2, btn3)
        bot.reply_to(message, text='Главное меню', reply_markup=markup)
    else:
        text = 'Прости, я еще не научился вести диалог, но, возможно, и это я смогу делать :)'
        bot.reply_to(message, text)


if __name__ == '__main__':
    bot.infinity_polling()

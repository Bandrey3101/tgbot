from __future__ import print_function
import googleapiclient
import telebot
from telebot import types
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time
import traceback
import random
from telegram_bot_calendar import WMonthTelegramCalendar, LSTEP
import config
from dict import users

bot = telebot.TeleBot(config.token)

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'apikey.json'
calendarId = config.calendar_id

event_id = ''
back = types.KeyboardButton('В начало')
wrong_time = types.KeyboardButton('Изменить время')
wrong_date = types.KeyboardButton('Изменить дату')


@bot.message_handler(commands=['start'])
def start(message):
    name = f'Здравствуйте, {message.from_user.first_name}! Выберите услугу, на которую хотите записаться: '
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    manikur = types.KeyboardButton('Маникюр')
    pedicur = types.KeyboardButton('Педикюр')
    markup.add(manikur, pedicur, back)
    bot.send_message(message.chat.id, name, reply_markup=markup)
    print(message.chat.id)
    users[message.chat.id] = {}
    users[message.chat.id]["username"] = message.from_user.username
    users[message.chat.id]["first_name"] = message.from_user.first_name


@bot.message_handler(content_types=['contact'])
def getcontact(message):
    users[message.chat.id]["phone_num"] = message.contact.phone_number
    print(users[message.chat.id]["phone_num"])
    finish(message)


def start_calendar(message):
    calendarbot, step = WMonthTelegramCalendar(locale='ru', min_date=datetime.date.today() + datetime.timedelta(days=1),
                                               max_date=datetime.date.today() + datetime.timedelta(days=51)).build()
    bot.send_message(message.chat.id, f"Выберите день", reply_markup=calendarbot)


@bot.callback_query_handler(func=WMonthTelegramCalendar.func())
def calc(c):
    result, key, step = WMonthTelegramCalendar(locale='ru', min_date=datetime.date.today() + datetime.timedelta(days=1),
                                               max_date=datetime.date.today() + datetime.timedelta(days=51)).process(
        c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите день", c.message.chat.id, c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"День записи: {result.strftime('%d.%m.%Y')}", c.message.chat.id, c.message.message_id,
                              reply_markup=key)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        add_date = types.KeyboardButton('Верно!')
        wrong_date = types.KeyboardButton('Изменить дату')
        markup.add(add_date, wrong_date, back)
        bot.send_message(c.message.chat.id, 'Верно?', reply_markup=markup)
        users[c.message.chat.id]["booking_day"] = result.strftime('%d.%m.%Y')


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Маникюр' or message.text == 'Педикюр':
            users[message.chat.id]["event_summary"] = message.text
            print(users[message.chat.id]["event_summary"])
            start_calendar(message)
        elif message.text == 'Верно!':
            calendar.get_events_list2(message)
        elif message.text == 'Изменить дату':
            bot.send_message(message.chat.id, 'Давайте попробуем еще раз)')
            start_calendar(message)
        elif message.text in ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00']:
            users[message.chat.id]["booking_time"] = message.text
            getnumber(message)
        elif message.text == 'Изменить время':
            calendar.get_events_list2(message)
        elif message.text[0] == '+' or message.text[1] == '9' and len(message.text) == 11:
            users[message.chat.id]["phone_num"] = message.text
            finish(message)
        elif message.text == 'В начало':
            start(message)
        elif message.text == "Все верно!":
            random_id_event(message)
            print(message.chat.id)
            event = calendar.create_event_dict(message)
            calendar.create_event(event)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
            second_event = types.KeyboardButton('Записаться еще')
            delete = types.KeyboardButton('Отменить запись')
            markup.add(second_event, delete)
            bot.send_message(message.chat.id, 'Отлично, вы записаны! Благодарю за запись!\n'
                                              'Если у вас есть дополнительные вопросы, '
                                              'можете написать мне в личные сообщения @andreyblsv',
                             reply_markup=markup)
            time.sleep(1)
            bot.send_message(message.chat.id, 'Это тестовый бот, по воросам приобретения - пишите: @andreyblsv',
                             reply_markup=markup)
        elif message.text == 'Записаться еще':
            start(message)
        elif message.text == 'Отменить запись':
            calendar.get_events_id(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            second_event = types.KeyboardButton('Записаться еще')
            delete = types.KeyboardButton('Отменить запись')
            markup.add(second_event, delete)
            bot.send_message(message.chat.id, 'Больше записей не найдено! Жду вас снова)', reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(back)
            bot.send_message(message.chat.id,
                             'На этот вопрос я не знаю ответ. Воспользуйтесь, '
                             'пожалуйста, кнопками внизу или командой /start',
                             reply_markup=markup)


def getnumber(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    markup.add(reg_button, wrong_time, back)
    bot.send_message(message.chat.id,
                     'Оставьте свой контактный номер для связи, пожалуйста:',
                     reply_markup=markup)


def random_id_event(message):
    global event_id
    id_event = random.sample(range(10), 3)
    event_id = str(message.chat.id) + ''.join(map(str, id_event))
    print(event_id)


def get_dict(message):
    for k in users.keys():
        if k == message.chat.id:
            return users[k]


def finish(message):
    print(get_dict(message))
    print(get_dict(message)["first_name"])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    right_button = types.KeyboardButton("Все верно!")
    markup.add(right_button, wrong_time, wrong_date, back)
    bot.send_message(message.chat.id, f'{get_dict(message)["first_name"]}, вы записываетесь на '
                                      f'{get_dict(message)["event_summary"]}\n'
                                      f'{get_dict(message)["booking_day"]}\n'
                                      f'в {get_dict(message)["booking_time"]}\n'
                                      f'Ваш контактный номер: {get_dict(message)["phone_num"]}\n\n'
                                      f'Все верно?', reply_markup=markup)


def telegram_polling():
    try:
        bot.polling()
    except:
        traceback_error_string = traceback.format_exc()
        with open("Error.Log", "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime(
                "%c") + "\r\n<<ERROR polling>>\r\n" + traceback_error_string + "\r\n<<ERROR polling>>")
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


telegram_polling()

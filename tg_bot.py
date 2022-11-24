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
from telegram_bot_calendar import WMonthTelegramCalendar

bot = telebot.TeleBot('your token')
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'config.json'
calendarId = 'Your calendar id'

event_summary = ''
booking_day = ''
booking_time = ''
phone_num = ''
firstname = ''
username = ''
event_id = ''

t8 = types.KeyboardButton('8:00')
t10 = types.KeyboardButton('10:00')
t12 = types.KeyboardButton('12:00')
t14 = types.KeyboardButton('14:00')
t16 = types.KeyboardButton('16:00')
t18 = types.KeyboardButton('18:00')
back = types.KeyboardButton('Назад')


@bot.message_handler(commands=['start'])
def start(message):
    name = f'Hello, {message.from_user.first_name}! Я - бот-облегчитель забот, ' \
           f'могу записать тебя к лучшему на свете ' \
           f'мастеру.\nТебе просто надо выбртаь услугу: '
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    manikur = types.KeyboardButton('Маникюр')
    pedicur = types.KeyboardButton('Педикюр')
    markup.add(manikur, pedicur, back)
    bot.send_message(message.chat.id, name, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Маникюр' or message.text == 'Педикюр':
            global event_summary
            event_summary = message.text
            start_calendar(message)
        elif message.text == 'Абсолютно верно!':
            sendMessageForBookingTime(message)
        elif message.text == 'Вообще-то нет!':
            bot.send_message(message.chat.id, 'Давай попробуем еще раз)')
            start_calendar(message)
        elif message.text in ['8:00', '10:00', '12:00', '14:00', '16:00', '18:00']:
            global booking_time
            booking_time = message.text
            calendar.get_events_list(message)
        elif message.text[0] == '+' or message.text[1] == '9':
            global phone_num
            phone_num = message.text
            finish(message)
            # get_email(message)
        elif '@' in message.text:
            global user_email
            user_email = message.text
            finish(message)
        elif message.text == "Пропустить":
            finish(message)
        elif message.text == 'Назад':
            start(message)
        elif message.text == "Все верно!":
            global username, firstname
            username = message.from_user.username
            firstname = message.from_user.first_name
            random_id_event()
            event = calendar.create_event_dict()
            calendar.create_event(event)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
            second_event = types.KeyboardButton('Записаться еще')
            delete = types.KeyboardButton('Отменить запись')
            markup.add(second_event, delete)
            bot.send_message(message.chat.id, 'Ура! У нас всё получилось!\n'
                                              'Спасибо за запись, до встречи!\n'
                                              '\n'
                                              'Вопросы по разработке - @andrey0191', reply_markup=markup)
        elif message.text == 'Записаться еще':
            start(message)
        elif message.text == 'Отменить запись':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            second_event = types.KeyboardButton('Записаться еще')
            markup.add(second_event)
            bot.send_message(message.chat.id, 'Для отмены записи напиши, пожалуйста, '
                                              'дату и время в ЛС @andrey0191', reply_markup=markup)

        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(back)
            bot.send_message(message.chat.id,
                             'Что-то я тебя не пойму, воспользуйтся кнопаками внизу или командой /start',
                             reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def getcontact(message):
    global phone_num
    phone_num = message.contact.phone_number
    finish(message)


def start_calendar(message):
    calendarbot, step = WMonthTelegramCalendar(locale='ru', min_date=datetime.date.today(),
                                               max_date=datetime.date.today() + datetime.timedelta(days=50)).build()
    bot.send_message(message.chat.id, f"Выбери день", reply_markup=calendarbot)


@bot.callback_query_handler(func=WMonthTelegramCalendar.func())
def calc(c):
    result, key, step = WMonthTelegramCalendar(locale='ru', min_date=datetime.date.today(),
                                               max_date=datetime.date.today() + datetime.timedelta(days=50)).process(
        c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите день", c.message.chat.id, c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ты выбрала {result.strftime('%d.%m.%Y')}", c.message.chat.id, c.message.message_id,
                              reply_markup=key)
        global booking_day
        booking_day = str(result.strftime('%d.%m.%Y'))
        print(booking_day)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        add_date = types.KeyboardButton('Абсолютно верно!')
        wrong_date = types.KeyboardButton('Вообще-то нет!')
        markup.add(add_date, wrong_date, back)
        bot.send_message(c.message.chat.id, 'Верно?', reply_markup=markup)


def sendMessageForBookingTime(message):
    if booking_day == datetime.datetime.today().strftime('%d.%m.%Y') and int(
            datetime.datetime.now().strftime("%H")) < 8:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t8, t10, t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня:', reply_markup=markup)
    elif booking_day == datetime.datetime.today().strftime('%d.%m.%Y') and 10 > int(
            datetime.datetime.now().strftime("%H")) >= 8:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t10, t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня:', reply_markup=markup)
    elif booking_day == datetime.datetime.today().strftime('%d.%m.%Y') and 10 <= int(
            datetime.datetime.now().strftime("%H")) < 12:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня:', reply_markup=markup)
    elif booking_day == datetime.datetime.today().strftime('%d.%m.%Y') and 12 <= int(
            datetime.datetime.now().strftime("%H")) < 14:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня:', reply_markup=markup)
    elif booking_day == datetime.datetime.today().strftime('%d.%m.%Y') and 14 <= int(
            datetime.datetime.now().strftime("%H")) < 16:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня:', reply_markup=markup)
    elif booking_day == datetime.datetime.today().strftime("%Y-%m-%d") and 16 <= int(
            datetime.datetime.now().strftime("%H")) < 18:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня:', reply_markup=markup)
    elif booking_day == datetime.datetime.today().strftime("%Y-%m-%d") and int(
            datetime.datetime.now().strftime("%H")) >= 18:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(back)
        bot.send_message(message.chat.id, 'На сегодня записи больше нет', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t8, t10, t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, f'Доступное время на {booking_day}:', reply_markup=markup)



def getnumber(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    markup.add(reg_button, back)
    bot.send_message(message.chat.id,
                     'Оставь свой контактный номер для связи:',
                     reply_markup=markup)


def finish(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    right_button = types.KeyboardButton("Все верно!")
    markup.add(right_button, back)
    bot.send_message(message.chat.id,
                     f'Итак, {message.from_user.first_name}, ты записалась:\nна {event_summary}'
                     f'\n{booking_day}\nв {booking_time}\nтвой номер: {phone_num}\n\nВсе верно?',
                     reply_markup=markup)




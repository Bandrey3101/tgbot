import telebot
from telebot import types
import datetime


bot = telebot.TeleBot('token')

now = datetime.datetime.utcnow().isoformat()
current_time = datetime.datetime.now()
current_date_string = datetime.date.today()  # current_time.strftime('%d.%m')
current_hour = str(current_time)[11:13]

t8 = types.KeyboardButton('8:00')
t10 = types.KeyboardButton('10:00')
t12 = types.KeyboardButton('12:00')
t14 = types.KeyboardButton('14:00')
t16 = types.KeyboardButton('16:00')
t18 = types.KeyboardButton('18:00')
today = current_date_string
tomorrow = today + datetime.timedelta(days=1)
aftertomorrow = tomorrow + datetime.timedelta(days=1)
twoaftertomorrow = aftertomorrow + datetime.timedelta(days=1)
threaftertomorrow = twoaftertomorrow + datetime.timedelta(days=1)
today = today.strftime('%d.%m')
tomorrow = tomorrow.strftime('%d.%m')
aftertomorrow = aftertomorrow.strftime('%d.%m')
twoaftertomorrow = twoaftertomorrow.strftime('%d.%m')
threaftertomorrow = threaftertomorrow.strftime('%d.%m')
back = types.KeyboardButton('Назад')
#
# future_date = datetime.date.today() + datetime.timedelta(days=21)

event_summary = ''
booking_time = ''
booking_day = ''
phone_num = ''
firstname = ''
username = ''

def getdate(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton(today)
    btn2 = types.KeyboardButton(tomorrow)
    btn3 = types.KeyboardButton(aftertomorrow)
    btn4 = types.KeyboardButton(twoaftertomorrow)
    btn5 = types.KeyboardButton(threaftertomorrow)
    btn6 = types.KeyboardButton('Назад')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, 'На какой день хочешь записаться?', reply_markup=markup)



def sendInlineMessageForBookingTime(message):
    if booking_day == today and int(current_hour) < 8:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t8, t10, t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня', reply_markup=markup)
    elif booking_day == today and 10 > int(current_hour) >= 8:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t10, t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня', reply_markup=markup)
    elif booking_day == today and 10 <= int(current_hour) < 12:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня', reply_markup=markup)
    elif booking_day == today and 12 <= int(current_hour) < 14:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t14, t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня', reply_markup=markup)
    elif booking_day == today and 14 <= int(current_hour) < 16:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t16, t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня', reply_markup=markup)
    elif booking_day == today and  16 <= int(current_hour) < 18:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t18, back)
        bot.send_message(message.chat.id, 'Доступное время на сегодня', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(t8, t10, t12, t14, t16, t18, back)
        bot.send_message(message.chat.id, f'Доступное время на {booking_day}:', reply_markup=markup)

def finish(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    right_button = types.KeyboardButton("Все верно!")
    markup.add(right_button, back)
    bot.send_message(message.chat.id, f'Итак, {message.from_user.first_name}, ты записалась:\nна {event_summary}\n{booking_day}\nв {booking_time}\nтвой номер: {phone_num}\n\n Все верно?', reply_markup=markup)


def getnumber(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    markup.add(reg_button, back)
    bot.send_message(message.chat.id,
                     'Оставь свой контактный номер для связи:',
                     reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    name = f'Hello, {message.from_user.first_name}! Я - бот-обормот, могу записать тебя к лучшему на свете мастеру. Тебе просто надо выбртаь услугу:'
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
            getdate(message)
        elif message.text in (today, tomorrow, aftertomorrow, twoaftertomorrow, threaftertomorrow):
            global booking_day
            booking_day = message.text
            sendInlineMessageForBookingTime(message)
        elif message.text in ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00']:
            global booking_time
            booking_time = message.text
            getnumber(message)
        elif message.text[0] == '+' or '8' == message.text[0]:
            global phone_num
            phone_num = message.text
            finish(message)
        elif message.text == 'Назад':
            start(message)
        elif message.text == "Все верно!":
            global username, firstname
            username = message.from_user.username
            firstname = message.from_user.first_name
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
            second_event = types.KeyboardButton('Записаться еще')
            delete = types.KeyboardButton('Отменить запись')
            markup.add(second_event, delete)
            bot.send_message(message.chat.id, 'Спасибо за запись, до встречи!', reply_markup=markup)
        elif message.text == 'Записаться еще':
            start(message)
        elif message.text == 'Отменить запись':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            second_event = types.KeyboardButton('Записаться еще')
            markup.add(second_event)
            bot.send_message(message.chat.id, 'Твоя запись отменена, жду тебя снова)', reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def getcontact(message):
    global phone_num
    phone_num = message.contact.phone_number
    finish(message)


bot.polling(none_stop=True)


from Cart import Cart
import telebot
from telebot import types
import requests

import time

token = '1384569458:AAH4iyBPSnB77ekv0eA-hOpdCP7l6TsUJHY'
bot = telebot.TeleBot(token)

# url = 'http://127.0.0.1:8000/api/category/'
url = 'http://127.0.0.1:8000/api/'


@bot.message_handler(commands=['start'])
def start(message):
    # global cart
    # cart = Cart(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_1 = types.KeyboardButton('Каталог')
    key_2 = types.KeyboardButton('Корзина')
    key_3 = types.KeyboardButton('Заказы')
    key_4 = types.KeyboardButton('Контакты')
    markup.add(key_1, key_2, key_3, key_4)

    bot.send_message(message.chat.id,
                     text='a', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['Каталог', 'order'])
def da(call, order=None):
    try:
        data = call.data
        # call.data
    except:
        data = ''
    if data == 'Каталог':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)

        keyboard = types.InlineKeyboardMarkup()
        r = requests.get(url+'category')
        for category in r.json():
            if category['categories']:
                key = types.InlineKeyboardButton(
                    text=category['name'], callback_data=('cat_' + str(category['id'])))
                keyboard.add(key)

            # for category in r.json()['categories']:
            #     key = types.InlineKeyboardButton(
            #         text=category['name'], callback_data=category['id'])
            #     keyboard.add(key)
        bot.send_message(call.message.chat.id,
                         text='Выбери категорию', reply_markup=keyboard)
    elif data == 'order' or order:
        msg = bot.send_message(call.message.chat.id, 'Введите Ваше имя')
        bot.register_next_step_handler(msg, order)


@bot.message_handler(content_types=['text'])
def katalog(message):
    bot.delete_message(chat_id=message.chat.id,
                       message_id=message.message_id)

    cart = Cart(message.chat.id)
    text = message.text

    if text == 'Каталог':
        keyboard = types.InlineKeyboardMarkup()
        r = requests.get(url+'category')
        for category in r.json():
            if category['categories']:
                key = types.InlineKeyboardButton(
                    text=category['name'], callback_data=('cat_' + str(category['id'])))
                keyboard.add(key)

            # for category in r.json()['categories']:
            #     key = types.InlineKeyboardButton(
            #         text=category['name'], callback_data=category['id'])
            #     keyboard.add(key)
        bot.send_message(message.chat.id,
                         text='Выбери категорию', reply_markup=keyboard)
    elif text == 'Корзина':
        # bot.edit_message_text(chat_id=message.chat.id,
        #                message_id=message.message_id-1, text='test')
        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton(
            'Заказать', callback_data='order')
        key_2 = types.InlineKeyboardButton('Очистить', callback_data='clear')
        keyboard.add(key, key_2)
        t = [f"{prod['quantity']}x {prod['name']} - {prod['price']}р.  -  {prod['total_price']}р.\n" for prod in cart]
        t = 'Корзина\n\n' + '\n'.join(t) + \
            f'\nИтого: {cart.get_total_price()}р.'
        if cart:
            bot.send_message(message.chat.id, text=t, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, text=t)


def order(message):
    if message.text.isalpha():
        with open('db.json', 'r+') as file:
            data = json.load(file)
            cart = Cart(message.chat.id)
        cart['order'] = {
            # 'name': name
            # 'adress': adress
        }
    else:
        da('test', 1)

    # elif text == 'Заказы':/


@bot.callback_query_handler(func=lambda call: 'cat' in call.data.split('_'))
def callback_worker(call):
    id = call.data.split('_')[-1]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    r = requests.get(url+'category/'+id)
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(
        text='Назад', callback_data='Каталог')
    keyboard.add(key)

    for category in r.json()['categories']:
        key = types.InlineKeyboardButton(
            text=category['name'], callback_data='prods_'+str(category['id']))
        keyboard.add(key)
    bot.send_message(call.message.chat.id,
                     text='Выбери категорию', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'prods' in call.data.split('_'))
def prods(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    id = call.data.split('_')[-1]
    bot.last_update_id
    r = requests.get(url+'category/'+str(id))
    for prod in r.json()['products'][:5]:
        prod_id = prod['id']
        name = prod['name']
        price = prod['price']
        images = prod['images']
        images = 'https://im0-tub-ru.yandex.net/i?id=b6a2cf0ee7b2aafd66d4e996bab05433&n=13'

        keyboard = types.InlineKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(
            text='Добавить', callback_data='add_'+str(prod_id))
        key_2 = types.InlineKeyboardButton(
            text='Заказать в 1 клик', callback_data='add_'+str(prod_id))
        keyboard.add(key_1, key_2)
        img = [types.InputMediaPhoto(images, caption='test')
               for img in range(5)]
        # images[0]['image']
        bot.send_media_group(call.message.chat.id, img)
        bot.send_message(call.message.chat.id,
                         f'''{name}
{price}р.''', reply_markup=keyboard)

        time.sleep(0.3)


# ОТПРАВКА 1 IMG
#         bot.send_photo(call.message.chat.id, images, caption=f'''{name}
# {price}р.''', reply_markup=keyboard)

last_mes = None


@bot.callback_query_handler(func=lambda call: 'add' in call.data.split('_'))
def add(call):
    cart = Cart(call.message.chat.id)
    # bot.delete_message(call.message.chat.id, call.message.message_id)
    id = call.data.split('_')[-1]
    global last_mes
    prod = cart.add(id)
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(
        'Заказать', callback_data='order')
    key_2 = types.InlineKeyboardButton('Очистить', callback_data='clear')
    keyboard.add(key, key_2)
    # bot.edit_message_text('adsad', call.message.chat.id)
    # if prod['quantity'] == 1:
    #     t = [f"{prod['quantity']}x {prod['name']} - {prod['price']}р.\n" for prod in cart]
    #     t = '🛒 Продукты у Вас в корзине:\n\n' + '\n'.join(t) + \
    #         f'\nИтого: {cart.get_total_price()}р.'
    t = [
        f"{prod['quantity']}x {prod['name']} - {prod['price']}р.\n" for prod in cart]
    t = '🛒 Продукты у Вас в корзине:\n\n' + '\n'.join(t) + \
        f'\nИтого: {cart.get_total_price()}р.'

    try:
        if last_mes.message_id > call.message.message_id:
            bot.edit_message_text(t, call.message.chat.id,
                                  last_mes.message_id, reply_markup=keyboard)
        else:
            # bot.delete_message(last_mes.chat.id,last_mes.message_id)
            last_mes = bot.send_message(
                call.message.chat.id, t, reply_markup=keyboard)
    except:

        last_mes = bot.send_message(
            call.message.chat.id, t, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'clear' == call.data)
def clear(call):
    cart = Cart(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cart.clear()
    bot.send_message(call.message.chat.id, 'Корзина пуста')
#     else:
#         bot.edit_message_text(f'''🛒 Продукты у Вас в корзине:
# {prod['quantity']}x {prod['name']} - {prod['price']}р.
# Итого: {cart.get_total_price()}р.''',
#                               call.message.chat.id, call.message.message_id)


bot.polling(none_stop=True, interval=0)

# r = requests.get(url+'category/'+str(message.data))
# keyboard = types.InlineKeyboardMarkup()
# key = types.InlineKeyboardButton(
#     text='Назад', callback_data=call.data)
# keyboard.add(key)

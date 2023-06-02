from telegram import ReplyKeyboardMarkup, KeyboardButton, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import schedule
import time
import threading

from config import token
from db import *

bot = Bot(token=token)

# States
FIRST, SECOND, THIRD, FOURTH, FIVE, EXIT, FRIENDS = range(7)

# Keyboard
keyboard = [[KeyboardButton('Лечу')],
            [KeyboardButton('Отправляю')]]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)


def start(update, context):
    context.user_data.clear()
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    get_command(update, context)
    update.message.reply_text(
        'Я ваш SendIt Companion - бот-помощник по поиску компаньонов по перевозке важных и дорогих вам вещей.'
        ' Зарегистрируйтесь как путешественник чтобы попасть в мою базу, '
        'где вас смогут найти отправители. Всего 4 вопроса: "куда вы летите/едете", "откуда", "когда"'
        ' и "сколько хотите за доставку". Если вы отправитель то укажите откуда'
        '-куда вам нужно доставить вещи/документы и я найду для вас отзывчивых людей которым по пути! ')
    update.message.reply_text(
        'Я сохраню введенные данные и буду показывать их, в том числе ссылку на чат с вами, чтобы отправители могли'
        ' написать для уточнения деталей. Каждый пост хранится месяц - после чего удаляется из базы.')
    user = update.message.from_user
    context.user_data['username'] = user.first_name
    context.user_data['id'] = user.id
    update.message.reply_text('Привет, летите или отправляете?', reply_markup=reply_markup)
    return FIRST


def get_command(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    # elif text == '/start':
    #     return start(update, context)
    update.message.reply_text(
        'Список комманд:\n/start - запустить бота\n/cancel - завершить диалог\n/get_command - вызвать список команд\n/get_list_user - посмотреть свои путешествия')
    return ConversationHandler.END


def lechu(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    update.message.reply_text(
        'Куда летите?\n(пожалуйста укажите название города прибытия с большой буквы, например - "Cанкт-Петербург"')
    return SECOND


def otvet_second(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    context.user_data['куда'] = update.message.text
    update.message.reply_text(
        'Откуда?\n(пожалуйста укажите название города отправления с большой буквы, например - "Екатеринбург")')
    return THIRD


def otvet_third(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    context.user_data['откуда'] = update.message.text
    update.message.reply_text(
        'Когда?\n(укажите дату отбытия не позднее месяца от текущего времени в формате "04.12.2023")')
    return FOURTH


def otvet_fourth(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    context.user_data['когда'] = update.message.text
    update.message.reply_text(
        'Цена "спасибо"?\n(сколько вы хотите за доставку, например "500", указывайте сумму в рублях или "0"'
        ' если не хотите брать деньги. Так же поле может принимать текстовые значения например "шоколадку".)')
    return EXIT


def save_and_repeat(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    context.user_data['цена'] = update.message.text
    show_data(update, context)
    return ConversationHandler.END


def show_data(update, context):
    kuda = context.user_data.get('куда')
    otkuda = context.user_data.get('откуда')
    kogda = context.user_data.get('когда')
    price = context.user_data.get('цена')
    update.message.reply_text(
        f"Ваша поездка:\nМесто отправления: {otkuda}\nМесто назначения: {kuda}\nДата поездки: {kogda}\nЦена доставки:{price}")
    add_user_from_context(context.user_data)


def otpravlyayu(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    update.message.reply_text(
        'Откуда?\n(пожалуйста укажите название города отправления с большой буквы, например - "Екатеринбург")')
    return FIVE


def otvet_otpravlyayu(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    context.user_data['откуда'] = update.message.text
    update.message.reply_text(
        'Куда?\n(пожалуйста укажите название города, куда вы хотите отправить, с большой буквы, например - "Cанкт-Петербург"')
    return FRIENDS


def list_friends(update, context):
    text = update.message.text
    if text == '/cancel':
        update.message.reply_text('Диалог прерван')
        return ConversationHandler.END
    elif text == '/start':
        return start(update, context)
    context.user_data['куда'] = update.message.text
    friends = get_list(context.user_data)
    if not friends:
        update.message.reply_text("Пока никто не летит данным направлением")
        return ConversationHandler.END
    total = ''
    for friend in friends:
        kogda = friend[3]
        price = friend[4]
        user_chat_obj = bot.get_chat(chat_id=friend[6])
        user_chat_link = user_chat_obj.link
        update.message.reply_text(f"<a href='{user_chat_link}'>Летит: {friend[5]}</a>\nКогда: {kogda}\n'Cпасибо' в размре:{price}", parse_mode="HTML")
    return ConversationHandler.END


def get_list_user(update, context):
    user = update.message.from_user
    context.user_data['id'] = user.id
    my_list = get_my_list(context.user_data)
    if not my_list:
        update.message.reply_text("Вы пока никуда не летите")
        return ConversationHandler.END
    for post in my_list:
        update.message.reply_text(f"Откуда:{post[2]}\nКуда:{post[1]}\nКогда:{post[3]}\nЦена:{post[4]}")
    return ConversationHandler.END


def get_all(update, context):
    my_list = get_all_users()
    if not my_list:
        update.message.reply_text("Список пуст")
        return ConversationHandler.END
    for post in my_list:
        user_chat_obj = bot.get_chat(chat_id=post[6])
        user_chat_link = user_chat_obj.link
        update.message.reply_text(f"<a href='{user_chat_link}'>Летит: {post[5]}</a>\nОткуда:{post[2]}\nКуда:{post[1]}\nКогда:{post[3]}\nЦена:{post[4]}", parse_mode="HTML")
    return ConversationHandler.END


def run_delete_old_records():
    delete_old_records()


# Запуск функции каждый день в 3 часа ночи
schedule.every().day.at("03:00").do(run_delete_old_records)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


t = threading.Thread(target=run_schedule)
t.start()


def cancel(update, context):
    user = update.message.from_user
    context.user_data.clear()
    update.message.reply_text('Диалог завершен. /start чтобы начать новый диалог')
    return ConversationHandler.END


def main():
    # Create the Updater and dispatcher
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('get_command', get_command))
    dp.add_handler(CommandHandler('get_list_user', get_list_user))
    dp.add_handler(CommandHandler('get_all', get_all))
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [MessageHandler(Filters.regex('^Лечу$'), lechu),
                    MessageHandler(Filters.regex('^Отправляю$'), otpravlyayu)],
            SECOND: [MessageHandler(Filters.text, otvet_second)],
            THIRD: [MessageHandler(Filters.text, otvet_third)],
            FOURTH: [MessageHandler(Filters.text, otvet_fourth)],
            FIVE: [MessageHandler(Filters.text, otvet_otpravlyayu)],
            FRIENDS: [MessageHandler(Filters.text, list_friends)],
            EXIT: [MessageHandler(Filters.text, save_and_repeat)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

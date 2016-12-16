# -*- coding: utf-8 -*-
#
# EssexBot

import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from modules.exrate import ExRateRequestor
from modules.weather import WeatherRequestor
from modules.movies import MoviesRequestor

TOKEN = "286587089:AAEKSCnEp13jwzAc3TDH6Kv0114iCPCEAGI"
#TOKEN = "299609446:AAGk2Gwyr3s-OV_AGBXGVj6wKudVoG_yQoE"
PORT = int(os.environ.get("PORT", 5000))

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def get_start_message(bot, updater):
    updater.message.reply_text("Приветствую {}! Чем могу быть полезен?\n"
                              "\n"
                              "На данный момент, могу подсказать прогноз погоды на сегодня в Киеве,"
                              " а также актуальный курс валют.\n"
                              "\n"
                              "Если хочешь увидеть это сообщение еще раз - просто введи /help."
                              .format(updater.message.from_user.first_name))


def get_help_message(bot, updater):
    updater.message.reply_text("На данный момент, могу подсказать прогноз погоды на сегодня в Киеве,"
                              " а также актуальный курс валют.\n")


def get_value(user_input):
    """
    Return currency name from user input

    >>> get_value("доллар")
    'USD'
    >>> get_value("tdhj")
    False
    >>> get_value("")
    False
    >>> get_value(12)
    False
    """
    currencies = {"USD": ["usd", "дол"],
                  "EUR": ["eur", "евр"],
                  "RUB": ["rub", "руб"],
                  "UAH": ["uah", "грн", "гри"]}

    if isinstance(user_input, str):
        for key, value in currencies.items():
            if user_input[:3] in value:
                return key
    return False


def check_message(bot, updater):
    user_message = updater.message.text.lower().split(" ")
    print(user_message)

    for i in range(len(user_message)):
        # погода
        if "погода" in user_message[i]:
            updater.message.reply_text(WeatherRequestor().current_weather())

        # фильмы
        if user_message[i][:5] in ["фильм"]:
            if user_message[i - 1].isdigit():
                quantity = int(user_message[i - 1])
                top_movies = MoviesRequestor().get_actual_movie_list(limit=quantity)
                updater.message.reply_text("ТОП {} на сейчас:\n{}".format(quantity, top_movies))
            elif user_message[i - 2].isdigit():
                quantity = int(user_message[i - 2])
                top_movies = MoviesRequestor().get_actual_movie_list(limit=quantity)
                updater.message.reply_text("ТОП {} на сейчас:\n{}".format(quantity, top_movies))
            else:
                movies = MoviesRequestor().get_actual_movie_list()
                updater.message.reply_text("Самые популярные на данный момент:\n{}".format(movies))

        # курс валют
        if "валют" in user_message[i]:
            updater.message.reply_text(ExRateRequestor().show_required_currency())

        if "курс" in user_message[i] and get_value(user_message[i + 1]):        # Could be fixed - call 1 func 2 times
            currency = get_value(user_message[i + 1])
            currency_exrate = ExRateRequestor().show_required_currency(currency=currency)
            updater.message.reply_text("Актуальный курс на сейчас\n{}".format(currency_exrate))

        if user_message[i].isdigit() and get_value(user_message[i + 1]):
            amount = int(user_message[i])
            from_currency = get_value(user_message[i + 1])
            to_currency = get_value(user_message[i + 3])

            if from_currency and to_currency and (from_currency is "UAH" or to_currency is "UAH"):
                converted_amount = ExRateRequestor().convert_amount(amount, from_currency, to_currency)
                updater.message.reply_text("{} {}".format(converted_amount, to_currency))
            else:
                updater.message.reply_text("К сожалению, на данный момент, могу проводить конвертацию только"
                                           " с гривнами.")

        # другое
        if user_message[i] in ["привет", "здравствуй"]:
            updater.message.reply_text("Приветствую {}!".format(updater.message.from_user.first_name))


def main():
    # Main Updater with Webhook
    updater = Updater(TOKEN)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.setWebhook("https://essexbot.herokuapp.com/" + TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", get_start_message))
    dp.add_handler(CommandHandler("help", get_help_message))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, check_message))

    # Comment out the line below before commit
    #updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to provide basic BTC market information

import json
import requests
import os
from telegram import (ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ALERT, TODO_ADD_MORE = range(2)

BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE, DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW = range(10)


def btc(bot, update):
    r = requests.get('https://api.bitfinex.com/v2/ticker/tBTCUSD')

    btc_data = json.loads(r.text)

    price = btc_data[LAST_PRICE]
    daily_change = btc_data[DAILY_CHANGE]
    daily_change_perc = 100*btc_data[DAILY_CHANGE_PERC]
    low = btc_data[LOW]
    high = btc_data[HIGH]

    change = 'Desde ayer el precio '
    emoji = '\xF0\x9F\x93\x88'

    if daily_change > 0:
        change += 'subió'
    else:
        change += 'bajó'
        emoji = '\xF0\x9F\x93\x89'

    message = ('Precio actual\n${price:,.2f}\n\n'
               'Rango de hoy\n${low:,.2f} - ${high:,.2f}\n\n'
               '{change}\n${d:,.2f} {dp:,.2f}% {emoji}\n'
               .format(price=price, low=low, high=high, d=daily_change, dp=daily_change_perc, change=change, emoji=emoji))

    bot.send_message(chat_id=update.message.chat_id, text=message)

    return ConversationHandler.END


def alert(bot, update):
    update.message.reply_text('Bitcoin alerts coming soon!')

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ['TELEGRAM_TOKEN'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('btc', btc), CommandHandler('alert', alert)],

        states={
            ALERT: [MessageHandler(Filters.text, alert)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

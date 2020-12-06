import logging
from typing import Dict
import os
import requests
from telegram import ReplyKeyboardMarkup, Update,InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard1 = [
    ['politics', 'business','science'],
    ['world', 'us','arts'],
    ['Others']
]

reply_keyboard2 = [
    ['technology', 'travel','fashion'],
    ['food', 'health','opinion'],
    ['Back']
]

reply_keyboard3 = [
    ['News By Category'],
    ['Top 10 Read in the week']
]

reply_keyboard4 = [
    ['News By Category']
]

markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)
markup3 = ReplyKeyboardMarkup(reply_keyboard3, one_time_keyboard=True)
markup4 = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=True)


# def facts_to_str(user_data: Dict[str, str]) -> str:
#     facts = list()

#     for key, value in user_data.items():
#         facts.append(f'{key} - {value}')

#     return "\n".join(facts).join(['\n', '\n'])


# def start(update: Update, context: CallbackContext) -> int:
#     update.message.reply_text(
#         "Hi! Top news at your pocket",
#         reply_markup=markup1,
#     )
#     return CHOOSING

def start_with_inline(update: Update, context: CallbackContext) -> None:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user.username
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Welcome "+ user +"! \nSelect the options below to read news in your own way!", reply_markup=markup3)


def main_menu(update,context):
    update.message.reply_text("Select your way of news consumption",reply_markup=markup3)




def top10news(section_key='',categories=True):
    NYT_API_KEY = "YOUR_NYT_API_KEY"
    if categories:
        res = requests.get("https://api.nytimes.com/svc/topstories/v2/{}.json?api-key={}".format(section_key,NYT_API_KEY))
    else:
        res = requests.get("https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key={}".format(NYT_API_KEY))
    res_json = res.json()
    title = []
    short_url = []

    for item in res_json['results'][:10]:
        title.append(item['title'])
        if categories:
            short_url.append(item['short_url'])
        else:
            short_url.append(item['url'])
    if categories:
        text = "*Top 10 " + section_key +" News* \n"
    else:
        text ="*Top 10 read in the week* \n"
    text +="------------------------\n"
    
    for i in range(len(title)):
        text += str(i+1) +". " +title[i] +"\n"
        text += short_url[i]+ "\n"
    text +="\n_Powered by NYT API_"
    return text


def help(update,context):
    update.message.reply_text("Hello there! \n This is a news bot powered by New York Times (NYT) API, offering you a new way to consume news. \n/start to main menu \n/topread to read most viewed news in the week")


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    section = text
    topnews_text = top10news(section)
    update.message.reply_text(topnews_text, reply_markup=markup1 ,parse_mode="markdown")

def other_choice_display(update,context):
    update.message.reply_text("Other choices for selection",reply_markup=markup2,parse_mode="markdown")

def back_display(update,context):
    update.message.reply_text("Back to previous topics",reply_markup=markup1,parse_mode="markdown")

def other_choice(update,context):
    section = update.message.text
    topnews_text = top10news(section)
    update.message.reply_text(topnews_text, reply_markup=markup2 ,parse_mode="markdown")

def category_display(update,context):
    update.message.reply_text("Choose your favourite news categories, /start to main menu",reply_markup=markup1,parse_mode="markdown")

def top_read(update,context):
    topnews_text = top10news(categories=False)
    update.message.reply_text(topnews_text,reply_markup = markup4, parse_mode="markdown")








def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN ="YOUR_TELEGRAM_TOKEN"
    updater = Updater(TOKEN, use_context=True)

    # conv_handler= ConversationHandler(
    #         entry_points=[
    #            CommandHandler("start", start_with_inline)
    #         ],
    #         allow_reentry=True,
    #         states={
    #             1 : [CallbackQueryHandler(button,pattern='^(category|read)$' )],
    #         },
    #         fallbacks= []
    #     )
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    
    dispatcher.add_handler(CommandHandler("start", start_with_inline))
    dispatcher.add_handler(CommandHandler("help",help))
    dispatcher.add_handler(CommandHandler("topread",top_read))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(politics|science|us|arts|world|business)$'), regular_choice))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(Others)$'),other_choice_display))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(Back)$'),back_display))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(Main Menu)$'),main_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(News By Category)$'),category_display))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(Top 10 Read in the week)$'),top_read))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(opinion|technology|travel|fashion|food|health)$'), other_choice))

    PORT = int(os.environ.get('PORT', 5000))
   
    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://agile-chamber-12700.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

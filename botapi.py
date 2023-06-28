from telegram import Update,InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, CallbackContext, filters, CallbackQueryHandler
import database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from uuid import uuid4
from config import botTOKEN


def start(update: Update, context: CallbackContext) -> None:

    user = update.effective_user
    update.message.reply_markdown_v2(f'''*Hi {user.mention_markdown_v2()}\!

I return JSON responses of both bot api and MTProto for your messages\.

Hit help to know more about how to use me\.
	
	*''',
                                     reply_markup=InlineKeyboardMarkup([[
                                         InlineKeyboardButton(
                                             "HELP", callback_data="getHELP"),
                                     ]]))


def help(update: Update, context: CallbackContext) -> None:

    update.message.reply_markdown_v2(
        f'''
Here is a detailed guide to use me\.
You can use me to get JSON responses of your messages\.

*Supports:*
   \- `Messages`
   \- `Inline Query`
   \- `Callback Query`
   

Use /set to switch between `bot API` and `MTProto` mode and /button to generate sample inline keyboard buttons\.
''',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Get Help",
                                 url="https://t.me/ostrichdiscussion"),
        ]]))


def button(update: Update, context: CallbackContext) -> None:

    update.message.reply_markdown_v2(
        f'''
*Sample Inline Buttons:*
''',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Button1", callback_data="button1"),
        ], [
            InlineKeyboardButton("Button2", callback_data="Button2"),
        ]]))


def set_mode(update: Update, context: CallbackContext):
    update.message.reply_markdown_v2(
        text=f"*Select an option*",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("bot API", callback_data="set_botapi"),
        ], [
            InlineKeyboardButton("MTProto", callback_data="set_mtproto"),
        ]]),
        reply_to_message_id=update.message.message_id)


def new_message(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id == 1763185727:
        return
    update.message.reply_text(f"<code>{update}</code>", parse_mode="html")


def copy(update: Update, context: CallbackContext) -> None:
    context.bot.copy_message(chat_id=update.message.chat.id,
                 from_chat_id=update.message.chat_id,
                 message_id=update.message.reply_to_message.message_id,
                 reply_markup=update.message.reply_to_message.reply_markup)

class ModeFilter(filters.UpdateFilter):
    def filter(self, update: Update) -> bool:

        keys = dir(update)

        if "message" in keys:
            user = update.message.chat.id
        elif "inline_query" in keys:
            user = update.inline_query["from"].id
        else:
            print(keys)

        mode = database.find_mode(user)
        return mode == 'botapi'


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bot API response",
            description="@responseJSONbot",
            input_message_content=InputTextMessageContent(f"{update}")),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="About",
            description="@responseJSONbot",
            url="https://t.me/theostrich",
            input_message_content=InputTextMessageContent(f"{update}"),
        ),
    ]

    update.inline_query.answer(results)


def callback(update: Update, context: CallbackContext) -> None:
    if update.callback_query.message:
        user = update.callback_query.message.chat.id
    else:
        user = update.callback_query["from"].id
    mode = database.find_mode(update.callback_query.message.chat.id)
    if mode == 'botapi':
        query = update.callback_query

        if query.data.startswith('set'):
            query.answer()
            mode = query.data.split("_")[1]
            database.set_mode(user, mode)
            query.message.reply_text(text=f"*Mode set to {mode} successfully*",
                                     parse_mode="MARKDOWNV2")

        elif query.data.startswith('getHELP'):

            query.answer()
            query.message.edit_text(
                text=f'''
Here is a detailed guide to use me\.
You can use me to get JSON responses of your messages\.

*Supports:*
   \- `Messages`
   \- `Inline Query`
   \- `Callback Query`
   
Use /set to switch between `bot API` and `MTProto` mode\.
''',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Get Help",
                                         url="https://t.me/ostrichdiscussion"),
                ]]),
                parse_mode="MARKDOWNV2",
                disable_web_page_preview=True)
        elif query.data == "closeInline":
            query.message.delete_message()
        else:
            try:
                context.bot.send_message(
                    chat_id=user,
                    text=f"<code>{update}</code>",
                    parse_mode='html',
                    disable_web_page_preview=True,
                    disable_notification=True,
        
                )
            except:
                file = open("json.txt", "w+")
                file.write(f"{update}")
                file.close()
                context.bot.send_document(chat_id=user,
                                          document="json.txt",
                                          caption="responseJSONbot",
                                          disable_notification=True)


def main() -> None:
    updater = Updater(botTOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start, ModeFilter()))
    dispatcher.add_handler(CommandHandler("help", help, ModeFilter()))
    dispatcher.add_handler(CommandHandler("copy", copy, ModeFilter()))
    dispatcher.add_handler(CommandHandler("button", button, ModeFilter()))
    dispatcher.add_handler(CommandHandler("set", set_mode, ModeFilter()))
    dispatcher.add_handler(CallbackQueryHandler(callback))

    dispatcher.add_handler(InlineQueryHandler(inlinequery, ModeFilter()))
    dispatcher.add_handler(MessageHandler(ModeFilter(), new_message))

    updater.start_polling()
    updater.idle()

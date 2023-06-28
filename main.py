from multiprocessing import Process
import botapi
from pyrogram import Client, filters
import json
import database
import alive
from pyrogram.errors import MessageTooLong
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from config import apiID, apiHASH, botTOKEN
import time
import pymongo
import os


async def func(_, __, m):
  if m.from_user.is_self:
    return False

  json_object = json.loads(f"{m}")
  instance = json_object["_"]

  if instance == "Message":
    user = m.chat.id
    chattype = m.chat.type
  elif instance == "CallbackQuery":
    user = m.message.chat.id
    chattype = m.message.chat.type

  elif instance == "InlineQuery":
    user = m.from_user.id
    chattype = "private"
  else:
    print(instance)

  if not database.user_exist(user, chattype):
    database.scrape(m)

  mode = database.find_mode(user)

  return mode == "mtproto"


mode_filter = filters.create(func)

ostrich = Client("ostrich", api_id=apiID, api_hash=apiHASH, bot_token=botTOKEN)


@ostrich.on_message(filters.command(["button"]) & mode_filter)
async def buttons(client, message):
  await message.reply_text(text='**Sample Inline buttons:**',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup([
                             [
                               InlineKeyboardButton("Button1",
                                                    callback_data="Button1"),
                             ],
                             [
                               InlineKeyboardButton("Button2",
                                                    callback_data="Button2"),
                             ],
                           ]),
                           reply_to_message_id=message.id)


@ostrich.on_message(filters.command(["help"]) & mode_filter)
async def help(client, message):

  await message.reply_text(text=f'''
Here is a detailed guide to use me.
You can use me to get JSON responses of your messages.

**Supports:**
   - `Messages`
   - `Inline Query`
   - `Callback Query`

Use /set to switch between `bot API` and `MTProto` mode and /button to generate sample inline keyboard buttons.''',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup([[
                             InlineKeyboardButton(
                               "Get Help",
                               url="https://t.me/ostrichdiscussion/"),
                           ]]),
                           reply_to_message_id=message.id)


@ostrich.on_message(filters.command(["start"]) & mode_filter)
async def start(client, message):

  await message.reply_text(text=f'''
**Hi {message.from_user.mention}!

I return JSON responses of both bot api and MTProto for your messages.

Hit help to know more about how to use me.
	
	**''',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup([[
                             InlineKeyboardButton("HELP",
                                                  callback_data="getHELP"),
                           ]]),
                           reply_to_message_id=message.id)
  database.scrape(message)


@ostrich.on_message(filters.command(["copy"]) & mode_filter)
async def copy(client, message):
  await client.copy_message(message.chat.id,
                            message.chat.id,
                            message.reply_to_message.id,
                            reply_markup=message.reply_to_message.reply_markup)


@ostrich.on_message(filters.command(["set"]) & mode_filter)
async def set(client, message):

  await message.reply_text(
    text="**Select an option**",
    disable_web_page_preview=True,
    reply_markup=InlineKeyboardMarkup([[
      InlineKeyboardButton("bot API", callback_data="set_botapi"),
    ], [
      InlineKeyboardButton("MTProto", callback_data="set_mtproto"),
    ]]),
    reply_to_message_id=message.id)


@ostrich.on_message(mode_filter)
async def new_message(client, message):

  json_object = json.loads(f"{message}")
  formatted = json.dumps(json_object, indent=4)
  try:
    await message.reply_text(
      f"```{formatted}```",
      disable_web_page_preview=True,
      disable_notification=True,
    )
  except MessageTooLong:
    file = open("json.txt", "w+")
    file.write(formatted)
    file.close()
    await client.send_document(message.chat.id,
                               document="json.txt",
                               caption="responseJSONbot",
                               disable_notification=True)


@ostrich.on_chosen_inline_result(mode_filter)
async def inline_result(client, inline_query):

  mode = database.find_mode(inline_query.from_user.id)
  if mode != "mtproto":
    print(
      f"ignoring non mtproto request by user {inline_query.from_user.id.first_name}"
    )
    return
  json_object = json.loads(f"{inline_query}")
  formatted = json.dumps(json_object, indent=4)
  try:
    await client.send_message(
      chat_id=inline_query.from_user.id,
      text=f"```{formatted}```",
      disable_web_page_preview=True,
      disable_notification=True,
    )
  except MessageTooLong:
    file = open("json.txt", "w+")
    file.write(formatted)
    file.close()
    await client.send_document(document="json.txt",
                               caption="responseJSONbot",
                               disable_notification=True,
                               quote=True)


@ostrich.on_inline_query(mode_filter)
async def inline_query(client, inline_query):
  await inline_query.answer(results=[
    InlineQueryResultArticle(title="MTProto API response",
                             input_message_content=InputTextMessageContent(
                               f"{inline_query}"),
                             description="@responseJSONbot",
                             thumb_url="https://i.imgur.com/JyxrStE.png"),
    InlineQueryResultArticle(
      title="About",
      input_message_content=InputTextMessageContent(
        "**Response JSON BOT - @ theostrich**"),
      url="https://t.me/theostrich",
      description="About bot",
      thumb_url="https://imgur.com/DBwZ2y9.png",
      reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton("Updates", url="https://t.me/ostrichdiscussion")
      ]])),
  ])


@ostrich.on_callback_query(mode_filter)
async def cb_handler(client, query):
  if query.data.startswith('set'):
    await query.answer()
    user = query.message.reply_to_message.chat.id
    mode = query.data.split("_")[1]
    database.set_mode(user, mode)
    await query.message.reply_text(text=f"**Mode set to {mode} successfully**")
  elif query.data == "getHELP":
    await query.answer()
    await query.message.edit_text(text=f'''
Here is a detailed guide to use me.
You can use me to get JSON responses of your messages.

**Supports:**
   - ```Messages```
   - ```Inline Query```
   - ```Callback Query```

Use /set to switch between ```bot API``` and ```MTProto``` mode and /button to generate sample inline keyboard buttons.
''',
                                  reply_markup=InlineKeyboardMarkup([[
                                    InlineKeyboardButton(
                                      "Get Help",
                                      url="https://t.me/ostrichdiscussion"),
                                  ]]),
                                  disable_web_page_preview=True)

  elif query.data == "closeInline":
    await query.answer("done")
    await query.message.delete()

  else:
    await query.answer()
    if query.message:
      user = query.message.chat.id
    else:
      user = query.from_user.id
    json_object = json.loads(f"{query}")
    formatted = json.dumps(json_object, indent=4)
    try:
      await client.send_message(user, text=f"```{formatted}```")
    except MessageTooLong:
      file = open("json.txt", "w+")
      file.write(formatted)
      file.close()
      await client.send_document(
        user,
        document="json.txt",
        caption="responseJSONbot",
        disable_notification=True,
      )


myclient = pymongo.MongoClient(os.environ['mongouri'])
db = myclient['JSONorg']
collection = db["usercache"]


@ostrich.on_message(filters.command(["broadcast"]))
async def broadcast(client, message):
  chat_id = message.chat.id
  botOwnerID = [1775541139, 1520625615]
  if chat_id in botOwnerID:
    await message.reply_text("Broadcasting...")
    chat = (collection.find({}, {'userid': 1, '_id': 0}))
    chats = [sub['userid'] for sub in chat]
    failed = 0
    for chat in chats:
      try:
        await message.reply_to_message.copy(chat)
        time.sleep(2)
      except:
        failed += 1
        print("Couldn't send broadcast to %s, group name %s", chat)
    await message.reply_text(
      "Broadcast complete. {} users failed to receive the message, probably due to being kicked."
      .format(failed))
  else:
    await client.send_message(
      1520625615, f"Someone tried to access broadcast command,{chat_id}")


if __name__ == '__main__':
  pyro = Process(target=ostrich.run)
  pyro.start()
  ptb = Process(target=botapi.main)
  ptb.start()
  web = Process(target=alive.run())
  web.start()
  pyro.join()
  ptb.join()
  web.join()


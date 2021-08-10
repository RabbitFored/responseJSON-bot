import pymongo
import json
from config import MongoDB_URI, database, collection

client = pymongo.MongoClient(MongoDB_URI)
db = client[collection['user']]


def scrape(data):
    userid = data.chat.id
    chattype = data.chat.type
    mycollection = db[collection['user']]

    if chattype == 'group' or chattype == "supergroup":
        mycollection = db[collection['group']]
        title = data.chat.title
    firstseen = data.date
    result = mycollection.find_one({'userid': userid})

    try:
        result['userid']
        userexist = True

    except:
        userexist = False

    username = data.from_user.username
    firstname = data.from_user.first_name
    lastname = data.from_user.last_name
    dc = data.from_user.dc_id

    scraped = {}
    scraped['userid'] = userid
    scraped['chattype'] = chattype

    if chattype == 'group' or chattype == "supergroup":
        scraped['title'] = title

    else:
        scraped['username'] = username
        scraped['firstname'] = firstname
        scraped['lastname'] = lastname
        scraped['is-banned'] = False
        scraped['dc'] = dc
    scraped['mode'] = "botapi"
    scraped['firstseen'] = firstseen

    if (userexist == False):
        mycollection.insert_one(scraped)


def find_mode(userid):
    mycollection = db[collection['user']]

    if userid < 0:
        mycollection = db[collection['group']]

    cursor = mycollection.find({'userid': userid})

    mode = "botapi"

    for i in cursor:
        mode = i['mode']

    return mode


def set_mode(userid, mode):
    mycollection = db[collection['user']]

    if userid < 0:
        mycollection = db[collection['group']]

    filter = {"userid": userid}
    values = {"$set": {"mode": mode}}
    mycollection.update(filter, values)


def user_exist(chatid, chattype):
    mycollection = db[collection['user']]

    if chattype == 'group' or chattype == "supergroup":
        mycollection = db[collection['group']]

    result = mycollection.find_one({'userid': chatid})
    try:
        result['userid']
        userexist = True

    except:
        userexist = False

    return userexist

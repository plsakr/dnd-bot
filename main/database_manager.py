from pymongo import MongoClient

client = MongoClient()
db = client.ddb_db

def retrieve_or_create_user(user_id):
    global db
    users = db.users
    retrieved = users.find_one({"_id":user_id})
    if retrieved == None:
        retrieved = {"_id": user_id, "chars":[], "active_char":""}
    return retrieved

def get_all_users():
    global db
    users = db.users
    return list(users.find())

def upsert_user(user):
    global db
    users = db.users
    users.replace_one({"_id":user["_id"]}, user, upsert=True)

def retrieve_char(char_id):
    global db
    chars = db.chars
    return chars.find_one({"_id":char_id})

def upsert_character(character):
    global db
    chars = db.chars
    chars.replace_one({"_id":character["_id"]}, character, upsert=True)

def exists_character_id(id):
    global db
    chars = db.chars
    return chars.find_one({"_id":id}) != None

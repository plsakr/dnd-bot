from pymongo import MongoClient, collection, ASCENDING
from bson.son import SON
import time


def measure_time(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('%r took %2.2f sec' % \
              (f.__name__, te - ts))
        return result

    return timed


client = MongoClient()
db = client.ddb_db


def init_db_connection(db_connection_string):
    global client
    global db
    client = MongoClient(db_connection_string)
    db = client.ddb_db


@measure_time
def retrieve_or_create_user(user_id):
    global db
    users = db.users
    retrieved = users.find_one({"_id": user_id})
    if retrieved == None:
        retrieved = {"_id": user_id, "chars": [], "active_char": ""}
    return retrieved


@measure_time
def get_all_users():
    global db
    users = db.users
    return list(users.find())


@measure_time
def upsert_user(user):
    global db
    users = db.users
    users.replace_one({"_id": user["_id"]}, user, upsert=True)


@measure_time
def retrieve_char(char_id):
    global db
    chars = db.chars
    return chars.find_one({"_id": char_id})


@measure_time
def upsert_character(character):
    global db
    chars = db.chars
    chars.replace_one({"_id": character["_id"]}, character, upsert=True)


@measure_time
def create_character(character):
    global db
    chars: collection = db.chars
    x = chars.insert_one(character)
    return x.inserted_id


@measure_time
def exists_character_id(id):
    global db
    chars = db.chars
    return chars.find_one({"_id": id}) != None


@measure_time
def add_spell(spell):
    global db
    spells = db.spells
    return spells.replace_one({"_id": spell["_id"]}, spell, upsert=True)


@measure_time
def retrieve_spell(name):
    global db
    spells = db.spells
    return spells.find_one({"_id": name})


@measure_time
def exists_spell(name):
    global db
    spells = db.spells
    return spells.find_one({"_id": name}) != None


@measure_time
def insert_monster(monster):
    global db
    monsters = db.monsters
    monsters.create_index([('name', ASCENDING)], unique=True)
    return monsters.insert_one(monster)


@measure_time
def insert_many_monsters(monster_objs, monster_grams):
    global db
    monsters = db.monsters
    mon_grams = db.monster_grams
    monster_ids = monsters.insert_many(monster_objs)
    gram_objs = []

    labels = ['ref', 'grams']
    for id, gram in zip(monster_ids.inserted_ids, monster_grams):
        gram_objs.append(dict(zip(labels, [id, gram])))

    mon_grams.insert_many(gram_objs)
    mon_grams.create_index([('grams', ASCENDING)])
    return monster_ids.inserted_ids


@measure_time
def does_monster_exist(name):
    global db
    monsters = db.monsters
    return monsters.find({'name': name}).limit(1).count() == 1


@measure_time
def does_monster_exist_id(bid):
    global db
    monsters = db.monsters
    return monsters.find({'_id': bid}).limit(1).count() == 1


@measure_time
def retrieve_monster(name):
    global db
    monsters = db.monsters
    return monsters.find_one({"name": name})


@measure_time
def retrieve_monster_id(bId):
    global db
    monsters = db.monsters
    return monsters.find_one({"_id": bId})


def retrieve_monster_name(bId):
    global db
    monsters = db.monsters
    return monsters.find_one({"_id": bId}, {'name': 1})['name']

def query_monster_grams(query):
    global db
    monster_grams: collection = db.monster_grams
    result = monster_grams.aggregate(
        [{'$match': {'grams': {'$in': query}}}, {'$project': {'ref': 1, 'grams': 1, 'score': {
            '$round': [
                {
                    '$divide': [
                        {
                            '$size': {
                                '$filter': {
                                    'input': "$grams",
                                    'cond': {
                                        '$in': ["$$this", query]
                                    }
                                }
                            }
                        }, {
                            '$size': "$grams"
                        }
                    ]
                }
                , 2]
        }}}, {'$sort': SON([('score', -1)])}, {'$limit': 10}])
    return list(result)

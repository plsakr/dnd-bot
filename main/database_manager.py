from pymongo import MongoClient, collection, ASCENDING, UpdateOne
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
    print(db_connection_string)
    client = MongoClient(db_connection_string)
    db = client.ddb_db
    return db


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


def delete_character(character_id):
    global db
    chars: collection = db.chars
    chars.delete_one({'_id': character_id})


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
    return bulk_insert_with_grams(mon_grams, monster_grams, monster_objs, monsters)


def bulk_insert_with_grams(grams_db, grams, docs, docs_db):
    gram_objs = []
    labels = ['ref', 'grams']
    write_operations = []
    for mon in docs:
        write_operations.append(UpdateOne({'name': mon['name']}, {'$setOnInsert': mon}, upsert=True))
    upsert_results = docs_db.bulk_write(write_operations)
    for index, _id in upsert_results.upserted_ids.items():
        gram_objs.append(dict(zip(labels, [_id, grams[index]])))
    if len(gram_objs) > 1:
        grams_db.insert_many(gram_objs)
        grams_db.create_index([('grams', ASCENDING)])
    return upsert_results.upserted_ids.values()


@measure_time
def insert_many_spells(spell_objs, spell_grams):
    global db
    spells = db.spells
    s_grams = db.spell_grams

    return bulk_insert_with_grams(s_grams, spell_grams, spell_objs, spells)

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
def does_spell_exist_id(bid):
    global db
    spells = db.spells
    return spells.find({'_id': bid}).limit(1).count() == 1


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


@measure_time
def retrieve_spell_id(bId):
    global db
    monsters = db.spells
    return monsters.find_one({"_id": bId})


def retrieve_monster_name(bId):
    global db
    monsters = db.monsters
    return monsters.find_one({"_id": bId}, {'name': 1})['name']


def retrieve_spell_name(bId):
    global db
    spells = db.spells
    return spells.find_one({"_id": bId}, {'name': 1})['name']


def retrieve_channel_combat(guild_id, channel_id):
    """
    Get the cached combat, if any, for a channel in a guild.
    :param guild_id: The id of the guild to search for
    :param channel_id: The id of the channel to search for
    :return: a combat object if it exists, or None.
    """
    global db
    settings = db.settings
    guild_doc = settings.find_one({"guild_id": guild_id})
    if guild_doc is not None:
        if 'combats' in guild_doc:
            combats = guild_doc['combats']
            if str(channel_id) in combats.keys():
                return combats[str(channel_id)]
    return None


def save_channel_combat(guild_id, channel_id, combat_object):
    global db
    settings = db.settings
    guild_doc = settings.find_one({"guild_id": guild_id})
    if guild_doc is not None:
        if 'combats' in guild_doc:
            if combat_object is None:
                guild_doc['combats'].pop(str(channel_id))
            else:
                guild_doc['combats'][str(channel_id)] = combat_object
        else:
            guild_doc['combats'] = {str(channel_id): combat_object}
    else:
        guild_doc = {'guild_id': guild_id, 'combats': {str(channel_id): combat_object}}
    settings.replace_one({"guild_id": guild_id}, guild_doc, upsert=True)


def retrieve_guild_prefix(guild_id, default_prefix):
    """
    Get the Guild's set prefix, or the default if one is not set.
    :param default_prefix: The default prefix to return if one is not set
    :param guild_id: The id of the guild to get the command prefix for
    :return: The prefix (as a string)
    """
    global db
    settings = db.settings
    guild_doc = settings.find_one({"guild_id": guild_id})
    if guild_doc is not None:
        if 'prefix' in guild_doc:
            return guild_doc['prefix']
        else:
            return default_prefix
    else:
        return default_prefix


def set_guild_prefix(guild_id, new_prefix):
    """
    Set a guild's new command prefix
    :param guild_id: The id of the guild that will be getting the new prefix
    :param new_prefix: The new command prefix for the guild
    :return: None
    """
    global db
    settings = db.settings
    guild_doc = settings.find_one({"guild_id": guild_id})
    if guild_doc is not None:
        guild_doc['prefix'] = new_prefix
    else:
        guild_doc = {'guild_id': guild_id, 'prefix': new_prefix}
    settings.replace_one({"guild_id": guild_id}, guild_doc, upsert=True)


def query_grams(query, collection_name):
    global db
    monster_grams = db[collection_name]
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

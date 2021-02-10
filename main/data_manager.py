import main.database_manager as db
import main.bot_spreadsheet as bs
import json
from main.cogs.search import create_grams

BOT_TOKEN = ""
GOOGLE_JSON_FILE = ""
MONGO_CONNECTION = ""


def init_global_data(is_test):
    print('beginning data initialization')
    global BOT_TOKEN
    global MONGO_CONNECTION
    with open("SECRETS.txt") as data_file:
        data = json.load(data_file)
        if not is_test:
            BOT_TOKEN = data['bot_token']
        else:
            BOT_TOKEN = data['test_token']
        MONGO_CONNECTION = data['mongo_connection']
    db.init_db_connection(MONGO_CONNECTION)
    _init_monster_data()


def get_all_users():
    return db.get_all_users()


def retrieve_char(query):
    return db.retrieve_char(query)


def exists_char_id(id):
    return db.exists_character_id(id)


def upsert_user(user):
    return db.upsert_user(user)


def upsert_character(character):
    return db.upsert_character(character)


def create_character(character):
    return db.create_character(character)


def retrieve_or_create_user(id):
    return db.retrieve_or_create_user(id)


def get_spell(name):
    if db.exists_spell(name):
        return db.retrieve_spell(name)
    else:
        spell_result = bs.search_spells(name)
        if spell_result['found'] == True:
            spell = __parse_result(spell_result)
            if spell['level'] != "#N/A":
                db.add_spell(spell)
            return spell
        else:
            return None


def get_monster(name):
    if db.does_monster_exist(name):
        return db.retrieve_monster(name)
    else:
        return None


def get_monster_by_id(bId):
    if db.does_monster_exist_id(bId):
        return db.retrieve_monster_id(bId)


def get_monster_choices(query_grams):
    results = db.query_monster_grams(query_grams)
    names = []
    if len(results) > 0:
        ids = [r['ref'] for r in results]
        names = [db.retrieve_monster_name(i) for i in ids]

    return results, names




def __parse_result(spell_result):
    spell_result = spell_result['value']
    spell = {}
    spell['_id'] = spell_result[0]
    spell['level'] = spell_result[1]
    spell['school'] = spell_result[2]
    spell['cast_time'] = spell_result[3]
    spell['is_ritual'] = spell_result[4]
    spell['duration'] = spell_result[5]
    spell['rng'] = spell_result[6]
    spell['components'] = spell_result[7]
    spell['description'] = spell_result[8]
    spell['ref'] = spell_result[9]

    return spell


def _init_monster_data():
    print('initializing monster data')
    with open('./data/monsters/index.json') as f:
        data = json.load(f)
        f.close()
        for filname in data['filenames']:
            with open('./data/monsters/'+filname) as mf:
                monster_data = json.load(mf)
                mf.close()
                all_monsters = monster_data['monster']

            if not db.does_monster_exist(all_monsters[0]['name']):
                grams = [create_grams(mon['name']) for mon in all_monsters]
                db.insert_many_monsters(all_monsters, grams)
                print('inserted ' + str(len(all_monsters)) + ' monsters')
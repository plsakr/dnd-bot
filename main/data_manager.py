import main.database_manager as db
import json
import os

from main.initiative import Initiative

BOT_TOKEN = ""
GOOGLE_JSON_FILE = ""
MONGO_CONNECTION = ""


def init_global_data(is_test):
    print('beginning data initialization')
    global BOT_TOKEN
    global MONGO_CONNECTION

    if not is_test:
        BOT_TOKEN = os.environ['BOT_TOKEN']
        MONGO_CONNECTION = os.environ['MONGO_CONNECTION']
    else:
        with open("SECRETS.txt") as data_file:
            data = json.load(data_file)
            if not is_test:
                BOT_TOKEN = data['bot_token']
            else:
                BOT_TOKEN = data['test_token']
            MONGO_CONNECTION = data['mongo_connection']
    db.init_db_connection(MONGO_CONNECTION)
    _init_monster_data()
    _init_spell_data()


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


def delete_character(char_id):
    return db.delete_character(char_id)


def retrieve_or_create_user(id):
    return db.retrieve_or_create_user(id)


def get_cached_combat(guild_id, channel_id):
    cached_obj = db.retrieve_channel_combat(guild_id, channel_id)
    if cached_obj is not None:
        return Initiative(cached_obj['players'],
                          cached_obj['current_init_index'],
                          cached_obj['start_battle'],
                          cached_obj['battle_round'],
                          cached_obj['cached_summary'],
                          cached_obj['dungeon_master'], )
    return None


def save_cached_combat(guild_id, channel_id, combat):
    db.save_channel_combat(guild_id, channel_id, combat)


def get_spell(name):
    if db.exists_spell(name):
        return db.retrieve_spell(name)
    else:
        # spell_result = bs.search_spells(name)
        # if spell_result['found'] == True:
        #     spell = __parse_result(spell_result)
        #     if spell['level'] != "#N/A":
        #         db.add_spell(spell)
        #     return spell
        # else:
        return None


def get_monster(name):
    if db.does_monster_exist(name):
        return db.retrieve_monster(name)
    else:
        return None


def get_monster_by_id(bId):
    if db.does_monster_exist_id(bId):
        return db.retrieve_monster_id(bId)


def get_spell_by_id(bId):
    if db.does_spell_exist_id(bId):
        return db.retrieve_spell_id(bId)


def get_monster_choices(query_grams):
    results = db.query_grams(query_grams, 'monster_grams')
    names = []
    if len(results) > 0:
        ids = [r['ref'] for r in results]
        names = [db.retrieve_monster_name(i) for i in ids]

    return results, names


def get_spell_choices(query_grams):
    results = db.query_grams(query_grams, 'spell_grams')
    names = []
    if len(results) > 0:
        ids = [r['ref'] for r in results]
        names = [db.retrieve_spell_name(i) for i in ids]

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

        for filename in data['filenames']:
            with open('./data/monsters/' + filename) as mf:
                monster_data = json.load(mf)
                mf.close()
                all_monsters = monster_data['monster']
                grams = [create_grams(mon['name']) for mon in all_monsters]
                db.insert_many_monsters(all_monsters, grams)


def _init_spell_data():
    print('initializing spell data')
    with open('./data/spells/index.json') as f:
        data = json.load(f)
        f.close()

        for filename in data['filenames']:
            with open('./data/spells/' + filename) as sf:
                spell_data = json.load(sf)
                sf.close()
                all_spells = spell_data['spell']
                grams = [create_grams(spell['name']) for spell in all_spells]
                db.insert_many_spells(all_spells, grams)


def create_grams(query: str, n=3):
    actual = query.lower()
    words = actual.split(" ")
    out = []
    for w in words:
        length = len(w)
        for i in range(0, length, n):
            out.append(w[i:i + n])

    return out

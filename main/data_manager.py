import main.database_manager as db
import main.bot_spreadsheet as bs


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


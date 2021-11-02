### Manages all aspecs of character importing, updating, and communication with mongo/google drive
from d20 import roll, AdvType
import main.data_manager as data
import json
import xml.etree.ElementTree as ET


TEMP_FOLDER_NAME = "temp"
SKILLS = [
    'acr',
    'ani',
    'arc',
    'ath',
    'dec',
    'his',
    'ins',
    'inti',
    'inv',
    'med',
    'nat',
    'perc',
    'perf',
    'pers',
    'rel',
    'sle',
    'ste',
    'sur'
]

SKILL_NAMES = [
    'acrobatics',
    'animal handling',
    'arcana',
    'athletics',
    'deception',
    'history',
    'insight',
    'intimidation',
    'investigation',
    'medicine',
    'nature',
    'perception',
    'performance',
    'persuasion',
    'religion',
    'sleight of hand',
    'stealth',
    'survival'
]

MAIN_CHECKS = ['str', 'dex', 'con', 'int', 'wis', 'char']
MAIN_NAMES = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']

XML_FIELD_NAMES = ["PC Name", "HP Max", "AC", "Initiative bonus", "Str Mod", "Str ST Mod", "Dex Mod", "Dex ST Mod", "Con Mod",
                   "Con ST Mod", "Int Mod", "Int ST Mod", "Wis Mod", "Wis ST Mod", "Cha Mod", "Cha ST Mod", "Acr", "Ani",
                   "Arc", "Ath", "Dec", "His", "Ins", "Inti", "Inv", "Med", "Nat", "Perc", "Perf", "Pers", "Rel", "Sle",
                   "Ste", "Sur"]

character_data = {
    "name": "",
    "HPMax": 0,
    "ac": 0,
    "init": 0,
    "str": 0,
    "str_save": 0,
    "dex": 0,
    "dex_save": 0,
    "con": 0,
    "con_save": 0,
    "int": 0,
    "int_save": 0,
    "wis": 0,
    "wis_save": 0,
    "char": -0,
    "char_save": 0,
    "acrobatics": 0,
    "animal handling": 0,
    "arcana": 0,
    "athletics": 0,
    "deception": -0,
    "history": 0,
    "insight": 0,
    "intimidation": -0,
    "investigation": 0,
    "medicine": 0,
    "nature": 0,
    "perception": 0,
    "performance": -0,
    "persuasion": 0,
    "religion": 0,
    "sleight of hand": 0,
    "stealth": 0,
    "survival": 0,
}

STATUS_ERR_CHAR_EXISTS = -1
STATUS_OK = 0

STATUS_ERR = -99

STATUS_INVALID_INPUT = -98

active_players_and_characters = []


def load_data():
    global active_players_and_characters
    users = data.get_all_users()
    for user in users:
        player = {'user':user, 'char':data.retrieve_char(user['active_char']['id'])}
        active_players_and_characters.append(player)


def roll_check(user_id, check, adv = AdvType.NONE):
    global active_players_and_characters
    players = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))
    if len(players) == 0:
        return (STATUS_ERR, None)

    char = players[0]['char']
    if check.lower() in MAIN_CHECKS:
        dice = "1d20+{0}".format(char[check.lower()]).replace('+-', '-')

        result = roll(dice, advantage=adv)
        print('Rolled {0}. Result:{1}'.format(dice, result))

        ability = MAIN_NAMES[MAIN_CHECKS.index(check.lower())] if check.lower() in MAIN_CHECKS else SKILL_NAMES[
            SKILLS.index(check.lower().capitalize())]
        chatResult = 'Rolling **{0}** Check for {1}:\n'.format(ability, char['name'])
        chatResult = chatResult + str(result)
        return (STATUS_OK, chatResult)
    elif  check.lower() in SKILLS:
        dice = "1d20+{0}".format(char[SKILL_NAMES[SKILLS.index(check.lower())]]).replace('+-', '-')
        result = roll(dice, advantage=adv)
        print('Rolled {0}. Result:{1}'.format(dice, result))

        ability = MAIN_NAMES[MAIN_CHECKS.index(check.lower())] if check.lower() in MAIN_CHECKS else SKILL_NAMES[
            SKILLS.index(check.lower())]
        chatResult = 'Rolling **{0}** Check for {1}:\n'.format(ability, char['name'])
        chatResult = chatResult + str(result)
        return (STATUS_OK, chatResult)
    else:
        return (STATUS_INVALID_INPUT, None)


def roll_save(user_id, check, adv = AdvType.NONE):
    global active_players_and_characters
    players = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))
    if len(players) == 0:
        return (STATUS_ERR, None)

    char = players[0]['char']
    if check.lower() in MAIN_CHECKS:
        dice = "1d20+{0}".format(char[check.lower() + "_save"]).replace('+-', '-')

        result = roll(dice, advantage=adv)
        print('Rolled {0}. Result:{1}'.format(dice, result))

        ability = MAIN_NAMES[MAIN_CHECKS.index(check.lower())]
        chatResult = 'Rolling **{0}** Saving Throw for {1}:\n'.format(ability, char['name'])
        chatResult = chatResult + str(result)
        return (STATUS_OK, chatResult)
    else:
        return (STATUS_INVALID_INPUT, None)


def create_from_xml(xml_bytes):
    xml_string = xml_bytes.decode("utf-8")
    root = ET.fromstring(xml_string)

    if root.tag != '{http://ns.adobe.com/xfdf/}xfdf':
        return {}

    data = character_data.copy()

    data_keys = list(data.keys())
    for i in range(0, len(data_keys)):
        k = data_keys[i]
        data[k] = root.find('./{http://ns.adobe.com/xfdf/}fields/{http://ns.adobe.com/xfdf/}field[@name="' + XML_FIELD_NAMES[i] + '"]/{http://ns.adobe.com/xfdf/}value').text

    for k in data.keys():
        if k != 'name':
            try:
                data[k] = int(data[k])
            except ValueError:
                return {}
    data['HP'] = data['HPMax']

    # get all known spells
  #  spell_root = root.find('/{http://ns.adobe.com/xfdf/}fields/{http://ns.adobe.com/xfdf/}field[starts-with(@name,"P") and string-length(@name) =2]/{http://ns.adobe.com/xfdf/}field[@name="SSfront"]/{http://ns.adobe.com/xfdf/}field[@name="spells"]/{http://ns.adobe.com/xfdf/}field[@name="name"]')
    return data

def import_from_object(character, user_id):
    player = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))
    if len(player) == 1: # Found existing player! Check if this character exists
        player_chars = player[0]['user']['chars']
        characters = list(filter(lambda x: x['name'] == character['name'], player_chars))

        if len(characters) == 0: # Character does not exist!
            char_id = data.create_character(character)
            character['_id'] = char_id

            player[0]['user']['chars'].append({'id': char_id, 'name': character['name']})
            player[0]['user']['active_char'] = {'id': char_id, 'name': character['name']}
            player[0]['char'] = character
            data.upsert_user(player[0]['user'])
        else: # Character does exists! update info
            char_id = characters[0]['id']
            character['_id'] = char_id
            player[0]['user']['active_char'] = {'id': char_id, 'name': character['name']}
            player[0]['char'] = character

            data.upsert_user(player[0]['user'])
            data.upsert_character(character)

    else: # Did not find a player, create a new user, and assume the character needs to be created
        char_id = data.create_character(character)
        user = {
            "_id": user_id,
            "chars": [{'id': char_id, 'name': character['name']}],
            "active_char": {'id': char_id, 'name': character['name']}
        }
        new_player = {
            'user': user,
            'char': character
        }
        active_players_and_characters.append(new_player)
        data.upsert_user(user)

    print(character)
    return STATUS_OK

## DEPRECATED
def import_from_json(json_bytes, user_id):
    global active_players_and_characters
    print('Importing data from pdf!')

    json_string = json_bytes.decode("utf-8")
    character = json.loads(json_string)
    character['HP'] = character['HPMax']
    return import_from_object(character, user_id)


# def import_from_pdf(pdf_bytes, user_id):
#     global active_players_and_characters
#     print('Importing data from pdf!')
#     pages = convert_from_bytes(pdf_bytes, 350)
#
#     img_name = "./temp/page_0" + str(user_id) + ".jpg"
#     pages[0].save(img_name, "JPEG")
#
#     print(os.getcwd())
#     with open('./main/rectangles.json','r') as f:
#         rectangles = json.load(f)
#     rectangle_keys = ['name', 'HPMax', 'ac', 'init', 'str', 'dex', 'con', 'int', 'wis', 'char', 'str_save', 'dex_save',
#                       'con_save', 'int_save', 'wis_save', 'char_save', 'acrobatics', 'animal handling', 'arcana',
#                       'athletics', 'deception', 'history', 'insight', 'intimidation', 'investigation', 'medicine',
#                       'nature', 'perception', 'performance', 'persuasion', 'religion', 'sleight of hand', 'stealth',
#                       'survival']
#
#     im = cv2.imread(img_name)
#     character = {}
#     for i in range(len(rectangle_keys)):
#         key = rectangle_keys[i]
#         rect = rectangles[i]
#
#         cropped = im[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]
#         mask = cv2.inRange(cropped, (0, 0, 0), (50, 50, 50))
#         if key == 'name':
#             mask[55:, 650:] = 0.
#         mask = cv2.GaussianBlur(mask, (3, 3), 0)
#         mask = cv2.inRange(mask, 10, 255)
#         mask = np.bitwise_not(mask)
#         result = pytesseract.image_to_string(mask, 'eng', config='--psm 7')
#         result = result.replace('/', '7')
#         result = result.replace('\n\x0c', '')
#         result = result.replace('°', '')
#         result = result.replace('| ', '')
#         result = result.replace('=I', '-1')
#         try:
#             if not key == 'name':
#                 result = result.replace('.', '')
#                 result = int(result)
#         except ValueError:
#             print('!!!ERROR: Encountered an error while importing "{0}" as the {1}!!!'.format(result, key))
#             return STATUS_ERR
#         character[key] = result
#     character['HP'] = character['HPMax']
#     player = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))
#     if len(player) == 1: # Found existing player! Check if this character exists
#         player_chars = player[0]['user']['chars']
#         characters = list(filter(lambda x: x['name'] == character['name'], player_chars))
#
#         if len(characters) == 0: # Character does not exist!
#             char_id = data.create_character(character)
#             character['_id'] = char_id
#
#             player[0]['user']['chars'].append({'id': char_id, 'name': character['name']})
#             player[0]['user']['active_char'] = {'id': char_id, 'name': character['name']}
#             player[0]['char'] = character
#             data.upsert_user(player[0]['user'])
#         else: # Character does exists! update info
#             char_id = characters[0]['id']
#             character['_id'] = char_id
#             player[0]['user']['active_char'] = {'id': char_id, 'name': character['name']}
#             player[0]['char'] = character
#
#             data.upsert_user(player[0]['user'])
#             data.upsert_character(character)
#
#     else: # Did not find a player, create a new user, and assume the character needs to be created
#         char_id = data.create_character(character)
#         user = {
#             "_id": user_id,
#             "chars": [{'id': char_id, 'name': character['name']}],
#             "active_char": {'id': char_id, 'name': character['name']}
#         }
#         new_player = {
#             'user': user,
#             'char': character
#         }
#         active_players_and_characters.append(new_player)
#         data.upsert_user(user)
#
#     print(character)
#     return STATUS_OK


def switch_active_character(user_id, to_char_id):
    global active_players_and_characters
    player = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))[0]
    index = active_players_and_characters.index(player)
    if len(list(filter(lambda x: x['id'] == to_char_id, player['user']['chars']))) > 0:
        character = data.retrieve_char(to_char_id)
        player['user']['active_char'] = {'id': character['_id'], 'name': character['name']}
        player['char'] = character
        data.upsert_user(player['user'])
        active_players_and_characters[index] = player
        return True
    else:
        return False


def get_player_characters_list(user_id):
    user = data.retrieve_or_create_user(user_id)
    return user['chars']


def get_active_char(user_id):
    global active_players_and_characters
    players = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))

    if len(players) != 1:
        return (STATUS_ERR, None)

    return (STATUS_OK, players[0]['char'])


def update_character_hp(char, mod):
    char['HP'] += mod
    if char['HP'] < 0:
        char['HP'] = 0
    if char['HP'] > char['HPMax']:
        char['HP'] = char['HPMax']

    data.upsert_character(char)
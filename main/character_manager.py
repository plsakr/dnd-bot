### Manages all aspecs of character importing, updating, and communication with mongo/google drive
from d20 import roll, AdvType
import main.data_manager as data
from pdf2image import convert_from_bytes
import os
import json
import pytesseract
import numpy as np
import cv2

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



def import_from_pdf(pdf_bytes, user_id):
    global active_players_and_characters
    print('Importing data from pdf!')
    pages = convert_from_bytes(pdf_bytes, 350)

    img_name = "./temp/page_0" + str(user_id) + ".jpg"
    pages[0].save(img_name, "JPEG")

    print(os.getcwd())
    with open('./main/rectangles.json','r') as f:
        rectangles = json.load(f)
    rectangle_keys = ['name', 'HPMax', 'ac', 'init', 'str', 'dex', 'con', 'int', 'wis', 'char', 'str_save', 'dex_save',
                      'con_save', 'int_save', 'wis_save', 'char_save', 'acrobatics', 'animal handling', 'arcana',
                      'athletics', 'deception', 'history', 'insight', 'intimidation', 'investigation', 'medicine',
                      'nature', 'perception', 'performance', 'persuasion', 'religion', 'sleight of hand', 'stealth',
                      'survival']

    im = cv2.imread(img_name)
    character = {}
    for i in range(len(rectangle_keys)):
        key = rectangle_keys[i]
        rect = rectangles[i]

        cropped = im[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]
        mask = cv2.inRange(cropped, (0, 0, 0), (50, 50, 50))
        if key == 'name':
            mask[55:, 650:] = 0.
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        mask = cv2.inRange(mask, 10, 255)
        mask = np.bitwise_not(mask)
        result = pytesseract.image_to_string(mask, 'eng', config='--psm 7')
        result = result.replace('/', '7')
        result = result.replace('\n\x0c', '')
        result = result.replace('°', '')
        result = result.replace('| ', '')
        if not key == 'name':
            result = int(result)
        character[key] = result
    character['HP'] = character['HPMax']
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


def switch_active_character(user_id, to_char_id):
    global active_players_and_characters
    player = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))[0]
    index = active_players_and_characters.index(player)
    if len(list(filter(lambda x: x['id'] == to_char_id, player['user']['chars']))) > 0:
        character = data.retrieve_char(to_char_id)
        player['user']['active_char'] = {'id': character['_id'], 'name': character['PCName']}
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


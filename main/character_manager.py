### Manages all aspecs of character importing, updating, and communication with mongo/google drive
import main.helpers.pdf_downloader as pdf_downloader
import main.helpers.pdf_importer as pdf_importer
import os
# import main.database_manager as db
from d20 import roll, AdvType
import main.data_manager as data

TEMP_FOLDER_NAME = "temp"
SKILLS = [
    'Acr',
    'Ani',
    'Arc',
    'Ath',
    'Dec',
    'His',
    'Ins',
    'Inti',
    'Inv',
    'Med',
    'Nat',
    'Perc',
    'Perf',
    'Pers',
    'Rel',
    'Sle',
    'Ste',
    'Sur'
]

SKILL_NAMES = [
    'Acrobatics',
    'Animal Handling',
    'Arcana',
    'Athletics',
    'Deception',
    'History',
    'Insight',
    'Intimidation',
    'Investigation',
    'Medicine',
    'Nature',
    'Perception',
    'Performance',
    'Persuasion',
    'Religion',
    'Sleight of Hand',
    'Stealth',
    'Survival'
]

MAIN_CHECKS = ['str', 'dex', 'con', 'int', 'wis', 'cha']
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
    if check.lower() in MAIN_CHECKS or check.lower().capitalize() in SKILLS:
        dice = "1d20+{0}".format(char[check.lower()])

        result = roll(dice, advantage=adv)
        print('Rolled {0}. Result:{1}'.format(dice, result))

        ability = MAIN_NAMES[MAIN_CHECKS.index(check.lower())] if check.lower() in MAIN_CHECKS else SKILL_NAMES[SKILLS.index(check.lower().capitalize())]
        chatResult = 'Rolling **{0}** Check for {1}:\n'.format(ability, char['PCName'])
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
        dice = "1d20+{0}".format(char[check.lower() + "ST"])

        result = roll(dice, advantage=adv)
        print('Rolled {0}. Result:{1}'.format(dice, result))

        ability = MAIN_NAMES[MAIN_CHECKS.index(check.lower())]
        chatResult = 'Rolling **{0}** Saving Throw for {1}:\n'.format(ability, char['PCName'])
        chatResult = chatResult + str(result)
        return (STATUS_OK, chatResult)
    else:
        return (STATUS_INVALID_INPUT, None)

def import_from_drive_id(id, user_id):
    if data.exists_character_id(id):
        return STATUS_ERR_CHAR_EXISTS

    global active_players_and_characters
    create_temp_folder()

    # Download the character sheet:
    temp_file = TEMP_FOLDER_NAME + "/" + id + ".pdf"
    pdf_downloader.download_pdf(id, temp_file)
    print("PDF Download complete. Importing Character!")

    raw_data = pdf_importer.get_form_in_dict(temp_file)
    print("PDF Data imported, creating and uploading characters!")

    character = decode_character(raw_data, id)
    print("Character decoded!")
    # print(character)

    # os.remove(temp_file)
    players = list(filter(lambda x: x['user']['_id'] == user_id, active_players_and_characters))
    if len(players) == 1:
        players[0]['user']['chars'].append({'id':id, 'name':character['PCName']})
        players[0]['user']['active_char']={'id':id, 'name':character['PCName']}
        players[0]['char'] = character
        data.upsert_user(players[0]['user'])
    else:
        user = {
            "_id":user_id,
            "chars":[{'id':id, 'name':character['PCName']}],
            "active_char":{'id':id, 'name':character['PCName']}
        }
        player = {
            'user':user,
            'char':character
        }
        active_players_and_characters.append(player)
        data.upsert_user(user)

    data.upsert_character(character)
    return STATUS_OK
    # print(player)


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


def create_temp_folder():
    global TEMP_FOLDER_NAME
    try:
        os.mkdir(TEMP_FOLDER_NAME)
    except FileExistsError:
        print("temp folder exists. not recreating")

def decode_character(data, id):
    player = {"_id": id}
    player["PCName"] = data['PC Name']
    player['PlayerName'] = data['Player Name']
    player['InitBonus'] = int(data['Initiative bonus'])
    
    player['HPMax'] =  int(data['HP Max'])
    player['HP'] = player['HPMax']



    player['AC'] = int(data['AC'])

    player['str'] = int(data['Str Mod'])
    player['dex'] = int(data['Dex Mod'])
    player['con'] = int(data['Con Mod'])
    player['int'] = int(data['Int Mod'])
    player['wis'] = int(data['Wis Mod'])
    player['cha'] = int(data['Cha Mod'])

    player['strST'] = int(data['Str ST Mod'])
    player['dexST'] = int(data['Dex ST Mod'])
    player['conST'] = int(data['Con ST Mod'])
    player['intST'] = int(data['Int ST Mod'])
    player['wisST'] = int(data['Wis ST Mod'])
    player['chaST'] = int(data['Cha ST Mod'])

    player['PassPerc'] = int(data['Passive Perception'])

    for x in SKILLS:
        player[x.lower()] = int(data[x])

    return player


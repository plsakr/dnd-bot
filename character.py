import xmltodict

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

def import_character_from_json(input):
    j = xmltodict.parse(input)['xfdf']['fields']['field']

    player = {}
    advData = list(filter(lambda x: x['@name'] == 'AdvLog', j))[0]['field']

    player['PCName'] = list(filter(lambda x: x['@name'] == 'PC Name', advData))[0]['value']
    player['PlayerName'] = list(filter(lambda x: x['@name'] == 'Player Name', advData))[0]['value']
    player['InitBonus'] = list(filter(lambda x: x['@name'] == 'Initiative bonus', j))[0]['value']

    player['HPMax'] =  int(list(filter(lambda x: x['@name'] == 'HP Max', j))[0]['value'])
    player['HP'] = player['HPMax']

    player['AC'] = list(filter(lambda x: x['@name'] == 'AC', j))[0]['value']

    player['str'] = list(filter(lambda x: x['@name'] == 'Str Mod', j))[0]['value']
    player['dex'] = list(filter(lambda x: x['@name'] == 'Dex Mod', j))[0]['value']
    player['con'] = list(filter(lambda x: x['@name'] == 'Con Mod', j))[0]['value']
    player['int'] = list(filter(lambda x: x['@name'] == 'Int Mod', j))[0]['value']
    player['wis'] = list(filter(lambda x: x['@name'] == 'Wis Mod', j))[0]['value']
    player['cha'] = list(filter(lambda x: x['@name'] == 'Cha Mod', j))[0]['value']

    player['strST'] = list(filter(lambda x: x['@name'] == 'Str ST Mod', j))[0]['value']
    player['dexST'] = list(filter(lambda x: x['@name'] == 'Dex ST Mod', j))[0]['value']
    player['conST'] = list(filter(lambda x: x['@name'] == 'Con ST Mod', j))[0]['value']
    player['intST'] = list(filter(lambda x: x['@name'] == 'Int ST Mod', j))[0]['value']
    player['wisST'] = list(filter(lambda x: x['@name'] == 'Wis ST Mod', j))[0]['value']
    player['chaST'] = list(filter(lambda x: x['@name'] == 'Cha ST Mod', j))[0]['value']


    for x in SKILLS:
        player[x.lower()] = list(filter(lambda y: y['@name'] == x, j))[0]['value']

    print(player)
    return player

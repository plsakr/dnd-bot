import json
import xmltodict
import pprint
import character

f = open('Sahlo_data.xfdf', 'r')
xml = f.read()
p = character.import_character_from_json(xml)
# print(xml)
# j = xmltodict.parse(xml)['xfdf']['fields']['field']
# print('AC = ' + list(filter(lambda x: x['@name'] == 'AC', j))[0]['value'])
# advData = list(filter(lambda x: x['@name'] == 'AdvLog', j))[0]['field']
# print('PC Name = ' + list(filter(lambda x: x['@name'] == 'PC Name', advData))[0]['value'])
# print('Player Name = ' + list(filter(lambda x: x['@name'] == 'Player Name', advData))[0]['value'])
# print('Initiative = ' + list(filter(lambda x: x['@name'] == 'Initiative bonus', j))[0]['value'])

# print('Strength = ' + list(filter(lambda x: x['@name'] == 'Str Mod', j))[0]['value'])
# print('Dexterity = ' + list(filter(lambda x: x['@name'] == 'Dex Mod', j))[0]['value'])
# print('Constitution = ' + list(filter(lambda x: x['@name'] == 'Con Mod', j))[0]['value'])
# print('Intelligence = ' + list(filter(lambda x: x['@name'] == 'Int Mod', j))[0]['value'])
# print('Wisdom = ' + list(filter(lambda x: x['@name'] == 'Wis Mod', j))[0]['value'])
# print('Charisma = ' + list(filter(lambda x: x['@name'] == 'Cha Mod', j))[0]['value'])

# print('Strength ST= ' + list(filter(lambda x: x['@name'] == 'Str ST Mod', j))[0]['value'])
# print('Dexterity ST= ' + list(filter(lambda x: x['@name'] == 'Dex ST Mod', j))[0]['value'])
# print('Constitution ST= ' + list(filter(lambda x: x['@name'] == 'Con ST Mod', j))[0]['value'])
# print('Intelligence ST= ' + list(filter(lambda x: x['@name'] == 'Int ST Mod', j))[0]['value'])
# print('Wisdom ST= ' + list(filter(lambda x: x['@name'] == 'Wis ST Mod', j))[0]['value'])
# print('Charisma ST= ' + list(filter(lambda x: x['@name'] == 'Cha ST Mod', j))[0]['value'])



# res = json.dumps(j).replace('@name', 'name')
# o = open('test.json', 'w')
# o.write(res)
# o.close()
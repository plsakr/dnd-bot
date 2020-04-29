import discord
import random
from d20 import roll, RollResult, AdvType
import urllib.request
import bot_spreadsheet
import message_formatter
import main.character_manager as cm
from pymongo import MongoClient
from main.initiative import Initiative, Combatant

TOKEN = 'NzAxODQxMjE1MzA5NzQyMTIw.Xp3Www.aeQE74SSNa_J0yzcN-FgAmcYfn8'

mongoC = MongoClient()
db = mongoC.ddb_db

cached_combat = None

SEARCH_TYPES = ['spell']

class MyClient(discord.Client):
    async def on_ready(self):
        bot_spreadsheet.init()
        print('Logged on as {0}'.format(self.user))

    async def on_message(self, message):
        if message.author == self.user:
            return

        print('Message from {0.author}: {0.content}'.format(message))

        if message.content.startswith('?'):
            await execute_command(message)

async def execute_command(message):
    commands = message.content.split()
    if commands[0] == '?r':
        await roll_a_dice(commands, message)

    elif commands[0] == '?chimport':
        if len(commands) == 1:
            await message.channel.send("Please input the public pdf url!")
            return
        url = commands[1]
        id = url.split("id=")[1]
        await message.channel.send("Importing character. Please wait ~~a while because miguel wants me to import from a pdf directly~~ :p")
        print("Importing from id: " + id)
        status = cm.import_from_drive_id(id, message.author.id)
        # cha = character.import_character_from_json((await message.attachments[0].read()).decode('utf-8'))
        # cha['_id'] = message.author.id
        # db.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
        if status == cm.STATUS_OK:
            x, char = cm.get_active_char(message.author.id)
            await message.channel.send('Imported ' + char['PCName'])
        elif status == cm.STATUS_ERR_CHAR_EXISTS:
            await message.channel.send('A Character has already been imported from that url. If you need to update it, use `?chupdate` instead!')

    elif commands[0] == '?check':
        await check(commands, message)

    elif commands[0] == '?save':
        await save(commands, message)

    elif commands[0] == '?i':
        await initiative(commands, message)

    elif commands[0] == '?hp':
        await hp(commands, message)

    elif commands[0] == '?spell':
        await search('spell', commands, message)

async def roll_a_dice(commands, message):
    try:
        term = ""
        for i in range(1, len(commands)):
            term += commands[i]
        result = roll(term) if term != 'd420' else '69'
        print('Rolled {0}. Result:{1}'.format(term, str(result) if type(result) == RollResult else result))
        chatResult = 'Rolling {0}:\n'.format(term)
        chatResult = chatResult + '{0}'.format(str(result) if type(result) == RollResult else result)
        await message.channel.send(chatResult)
    except:
        await message.channel.send('Invalid syntax. Check out correct syntax at: d20 library readme')

async def check(commands, message):
    adv = AdvType.NONE
    if len(commands) > 2:
        if 'adv' in commands[2].lower():
            adv = AdvType.ADV
        elif 'dis' in commands[2].lower():
            adv = AdvType.DIS
        
    status, result = cm.roll_check(message.author.id, commands[1], adv)
    print(status)
    print(result)
    if status == cm.STATUS_OK:
        chatResult = message.author.mention + ":game_die: " + result
        await message.channel.send(chatResult)
    elif status == cm.STATUS_ERR:
        await message.channel.send('use ?chimport first!')
    elif status == cm.STATUS_INVALID_INPUT:
        await message.channel.send('Not a valid check!')

async def save(commands, message):
    adv = AdvType.NONE
    if len(commands) > 2:
        if 'adv' in commands[2].lower():
            adv = AdvType.ADV
        elif 'dis' in commands[2].lower():
            adv = AdvType.DIS
        
    status, result = cm.roll_save(message.author.id, commands[1], adv)
    print(status)
    print(result)
    if status == cm.STATUS_OK:
        chatResult = message.author.mention + ":game_die: " + result
        await message.channel.send(chatResult)
    elif status == cm.STATUS_ERR:
        await message.channel.send('use ?chimport first!')
    elif status == cm.STATUS_INVALID_INPUT:
        await message.channel.send('Not a valid check!')

async def roll_initiative(message, cha = None, initBonus = None, private = False):
    try:
        result = roll("1d20+{0}".format(cha['InitBonus'] if cha != None else initBonus))
        print('Rolled for initiative. Result:{0}'.format(result.total))
        chatResult = '{0} Rolling for Initiative:\n'.format(message.author.mention)
        chatResult = chatResult + '{0}'.format(str(result))
        if private == False:
            await message.channel.send(chatResult)
        else:
            await message.author.send(chatResult)
        return result.total
    except:
        await message.channel.send('Invalid syntax. Check out correct syntax at: <http://tinyurl.com/pydice>')
        return 0

async def initiative(commands, message):
    global cached_combat
    if len(commands) > 1:
        if commands[1] == "begin":
            if cached_combat != None:
                await message.channel.send('Please end combat using `?i end` first!')
            else: #STARTING COMBAT
                print('Oh boy starting combat!!')
                cached_combat = Initiative()
                cached_combat.dungeon_master = message.author
                summary = cached_combat.get_full_text()
                await message.channel.send('Your DM has begun Combat! Join by typing `?i join`')
                cached_combat.cached_summary = await message.channel.send(summary)
                await cached_combat.cached_summary.pin()

        elif commands[1] == "end":
            if cached_combat == None:
                await message.channel.send('Combat has not started!')
            else:
                if cached_combat.dungeon_master != message.author:
                    await message.channel.send('Only the DM can end combat!!')
                else: #ENDING COMBAT
                    await cached_combat.cached_summary.delete()
                    cached_combat = None
                    await message.channel.send("Combat has ended. ~~Here's to the next TPK~~ :beers:")

        elif commands[1] == "join":
            if cached_combat == None:
                await message.channel.send('Combat has not started!')
            else: # Check if player has a player!
                status, cha = cm.get_active_char(message.author.id)
                if status == cm.STATUS_ERR:
                    await message.channel.send("You haven't imported a character!")
                else:
                    i = await roll_initiative(message, cha)
                    cbt = Combatant(cha['PCName'], i, message.author.mention, cha['HPMax'], cha['HP'])
                    print("ADDED A COMBATANT YA LATIF {0}".format(cbt))
                    cached_combat.add_char(cbt)
                    await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())

        elif commands[1] == "add":
            if cached_combat == None:
                await message.channel.send('Combat has not started!')
            else: 
                if cached_combat.dungeon_master != message.author:
                    await message.channel.send('Only the DM can add non player characters to combat!')
                else:
                    if len(commands) < 4:
                        print('NOT ENOUGH OPERANDS!')
                    else:
                        await message.delete()
                        i = await roll_initiative(message, None, commands[3], True)
                        cbt = Combatant(commands[2], i,None, int(commands[4]) if 0 <= 4 < len(commands) else None, None, private=True)
                        print("ADDED A COMBATANT YA LATIF {0}".format(cbt))
                        cached_combat.add_char(cbt)
                        await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())

        elif commands[1] == "hp":
            if cached_combat == None:
                await message.channel.send('Combat has not started!')
            else: 
                if cached_combat.dungeon_master != message.author:
                    await message.channel.send('Only the DM can edit NPC HP!')
                else:
                    if len(commands) < 4:
                        print('NOT ENOUGH OPERANDS!')
                    else:
                        cbt = cached_combat.get_combatant_from_name(commands[2])
                        cbt.modify_health(int(commands[3]))
                        await message.channel.send(cbt.get_summary())
                        await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())
                        await message.author.send(cbt.get_summary() + "Health: {}".format(cbt.current_hp))
                        await message.delete()

        elif commands[1] == "next":
            if cached_combat == None:
                await message.channel.send('Combat has not started!')
            else: 
                if cached_combat.dungeon_master != message.author:
                    await message.channel.send('Only the DM can edit NPC HP!')
                else:
                    current = cached_combat.next()
                    await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())
                    await message.channel.send("{0}{1} its your turn in initiative!".format(current.mention if current.mention != None else "", current.name))
                    

async def hp(commands, message):
    status, cha = cm.get_active_char(message.author.id)
    if status == cm.STATUS_ERR:
        message.channel.send("3mol ma3roof import a character first thanks!")
    else:
        if len(commands) == 1:
            await message.channel.send('{0}: {1}/{2}'.format(cha['PCName'], cha['HP'], cha['HPMax']))
        else:
            mod = int(commands[1])
            cha['HP'] += mod
            if cha['HP'] < 0:
                cha['HP'] = 0
            if cha['HP'] > cha['HPMax']:
                cha['HP'] = cha['HPMax']
            db.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
            if cached_combat == None:
                await message.channel.send('{0}: {1}/{2}'.format(cha['PCName'], cha['HP'], cha['HPMax']))
            else:
                cbt = cached_combat.get_combatant_from_name(cha['PCName'])
                cbt.modify_health(mod)
                await message.channel.send(cbt.get_summary())
                await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())

async def search(type, commands, message):
    if type in SEARCH_TYPES:
        term = ""
        for i in range(1, len(commands)):
            term += commands[i] + " "
        term = term.strip()
        if type == 'spell':
            print("Searching for " + term)
            result = bot_spreadsheet.search_spells(term)
            print("Result: ")
            print(result)
            if result["found"] == True:
                formatted_message = message_formatter.format_spell(result)
                await message.channel.send(embed=formatted_message)
            else:
                await message.channel.send("Could not find that spell. Please spell correctly!")





    else:
        await message.channel.send("That search has not been implemented yet. SORRY!")


print("Loading all saved data!")
cm.load_data()
client = MyClient()
client.run(TOKEN)


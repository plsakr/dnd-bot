import discord
import random
import rolldice
import urllib.request
import character
import bot_spreadsheet
import message_formatter
from pymongo import MongoClient
from initiative import Initiative, Combatant

TOKEN = 'NzAxODQxMjE1MzA5NzQyMTIw.Xp3Www.aeQE74SSNa_J0yzcN-FgAmcYfn8'

mongoC = MongoClient()
db = mongoC.ddb_db

cached_combat = None

MAIN_CHECKS = ['str', 'dex', 'con', 'int', 'wis', 'cha']
MAIN_NAMES = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']

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
        cha = character.import_character_from_json((await message.attachments[0].read()).decode('utf-8'))
        cha['_id'] = message.author.id
        db.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
        await message.channel.send('Imported ' + cha['PCName'])

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
        result, explanation = rolldice.roll_dice(commands[1])
        print('Rolled {0}. Result:{1}'.format(commands[1], result))
        chatResult = 'Rolling {0}:\n'.format(commands[1])
        if explanation == '[20]' and commands[1].contains('d20'):
            chatResult = chatResult + '***Crit!***\nNatural 20!'
        else:
            chatResult = chatResult + '{0} = {1}'.format(explanation, result)
        await message.channel.send(chatResult)
    except:
        await message.channel.send('Invalid syntax. Check out correct syntax at: <http://tinyurl.com/pydice>')

async def check(commands, message):
    if commands[1].lower() in MAIN_CHECKS or commands[1].lower().capitalize() in character.SKILLS:
        if db.chars.count_documents({'_id': message.author.id}, limit = 1) != 0:
            cha = db.chars.find_one({'_id': message.author.id})

            dice = "1d20+{0}".format(cha[commands[1].lower()])

            result, explanation = rolldice.roll_dice(dice)
            print('Rolled {0}. Result:{1}'.format(dice, result))

            ability = MAIN_NAMES[MAIN_CHECKS.index(commands[1].lower())] if commands[1].lower() in MAIN_CHECKS else character.SKILL_NAMES[character.SKILLS.index(commands[1].lower().capitalize())]
            chatResult = 'Rolling **{0}** Check for {1} {2}:\n'.format(ability, cha['PCName'], message.author.mention)
            chatResult = chatResult + '{0} = {1}'.format(explanation, result)
            
            await message.channel.send(chatResult)
        else:
            await message.channel.send('use ?chimport first!')
    else:
        await message.channel.send('Not a valid check!')

async def save(commands, message):
    if commands[1].lower() in MAIN_CHECKS:
        if db.chars.count_documents({'_id': message.author.id}, limit = 1) != 0:
            cha = db.chars.find_one({'_id': message.author.id})

            dice = "1d20+{0}".format(cha[commands[1].lower()+'ST'])

            result, explanation = rolldice.roll_dice(dice)
            print('Rolled {0}. Result:{1}'.format(dice, result))

            chatResult = 'Rolling {0} for {1} {2}:\n'.format(commands[1], cha['PCName'], message.author.mention)
            chatResult = chatResult + '{0} = {1}'.format(explanation, result)
            
            await message.channel.send(chatResult)
        else:
            await message.channel.send('use ?chimport first!')
    else:
        await message.channel.send('Not a valid save!')

async def roll_initiative(message, cha = None, initBonus = None, private = False):
    try:
        result, explanation = rolldice.roll_dice("1d20+{0}".format(cha['InitBonus'] if cha != None else initBonus))
        print('Rolled for initiative. Result:{0}'.format(result))
        chatResult = '{0} Rolling for Initiative:\n'.format(message.author.mention)
        chatResult = chatResult + '{0} = {1}'.format(explanation, result)
        if private == False:
            await message.channel.send(chatResult)
        else:
            await message.author.send(chatResult)
        return result
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

        elif commands[1] == "join":
            if cached_combat == None:
                await message.channel.send('Combat has not started!')
            else: # Check if player has a player!
                if db.chars.count_documents({'_id': message.author.id}, limit = 1) == 0:
                    await message.channel.send("You haven't imported a character!")
                else:
                    cha = db.chars.find_one({'_id': message.author.id})
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
    if db.chars.count_documents({'_id': message.author.id}, limit = 1) == 0:
        message.channel.send("3mol ma3roof import a character first thanks!")
    else:
        cha = db.chars.find_one({'_id': message.author.id})
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

client = MyClient()
client.run(TOKEN)


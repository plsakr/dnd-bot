import discord.ext.commands as commands
from d20 import AdvType, RollResult
from d20 import roll as d20_roll
from pymongo import MongoClient

import main.bot_spreadsheet as bs
import main.character_manager as cm
import main.message_formatter as mf
from main.initiative import Combatant, Initiative

import main.data_manager as dm

TOKEN = 'NzAxODQxMjE1MzA5NzQyMTIw.Xp3Www.aeQE74SSNa_J0yzcN-FgAmcYfn8'

mongoC = MongoClient()
db = mongoC.ddb_db


SEARCH_TYPES = ['spell']

bot = commands.Bot('?')

@bot.event
async def on_ready():
    bs.init()
    print('Logged on as {0}'.format(bot.user))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print('Message from {0.author}: {0.content}'.format(message))
    await bot.process_commands(message)

@bot.command()
async def chimport(ctx, arg):
    url = arg
    id = url.split("id=")[1]
    await ctx.send("Importing character. Please wait ~~a while because miguel wants me to import from a pdf directly~~ :p")
    print("Importing from id: " + id)
    status = cm.import_from_drive_id(id, ctx.author.id)
    # cha = character.import_character_from_json((await message.attachments[0].read()).decode('utf-8'))
    # cha['_id'] = message.author.id
    # db.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
    if status == cm.STATUS_OK:
        _, char = cm.get_active_char(ctx.author.id)
        await ctx.send('Imported ' + char['PCName'])
    elif status == cm.STATUS_ERR_CHAR_EXISTS:
        await ctx.send('A Character has already been imported from that url. If you need to update it, use `?chupdate` instead!')

@bot.command(aliases=['r'])
async def roll(ctx, *, arg):
    arg = arg.split(' ')
    try:
        term = ""
        for i in range(0, len(arg)):
            term += arg[i]
        result = d20_roll(term) if term != 'd420' else '69'

        # if ctx.author.id == miguel_id:
        #     result = 1
        print('Rolled {0}. Result:{1}'.format(term, str(result) if type(result) == RollResult else result))
        chatResult = 'Rolling {0}:\n'.format(term)
        chatResult = chatResult + '{0}'.format(str(result) if type(result) == RollResult else result)
        await ctx.send(chatResult)
    except:
        await ctx.send('Invalid syntax. Check out correct syntax at: d20 library readme')

@bot.command(aliases=['ch'])
async def check(ctx, *arg):
    adv = AdvType.NONE
    if len(arg) > 1:
        if 'adv' in arg[1].lower():
            adv = AdvType.ADV
        elif 'dis' in arg[1].lower():
            adv = AdvType.DIS
        
    status, result = cm.roll_check(ctx.author.id, arg[0], adv)
    print(status)
    print(result)
    if status == cm.STATUS_OK:
        chatResult = ctx.author.mention + ":game_die: " + result
        await ctx.send(chatResult)
    elif status == cm.STATUS_ERR:
        await ctx.send('use ?chimport first!')
    elif status == cm.STATUS_INVALID_INPUT:
        await ctx.send('Not a valid check!')

@bot.command(aliases=['s'])
async def save(ctx, *args):
    adv = AdvType.NONE
    if len(args) > 1:
        if 'adv' in args[1].lower():
            adv = AdvType.ADV
        elif 'dis' in args[1].lower():
            adv = AdvType.DIS
        
    status, result = cm.roll_save(ctx.author.id, args[1], adv)
    print(status)
    print(result)
    if status == cm.STATUS_OK:
        chatResult = ctx.author.mention + ":game_die: " + result
        await ctx.send(chatResult)
    elif status == cm.STATUS_ERR:
        await ctx.send('use ?chimport first!')
    elif status == cm.STATUS_INVALID_INPUT:
        await ctx.send('Not a valid check!')

async def roll_initiative(ctx, cha = None, initBonus = None, private = False):
    try:
        result = d20_roll("1d20+{0}".format(cha['InitBonus'] if cha != None else initBonus))
        print('Rolled for initiative. Result:{0}'.format(result.total))
        chatResult = '{0} Rolling for Initiative:\n'.format(ctx.author.mention)
        chatResult = chatResult + '{0}'.format(str(result))
        if private == False:
            await ctx.send(chatResult)
        else:
            await ctx.send(chatResult)
        return result.total
    except:
        await ctx.send('Invalid syntax. Check out correct syntax at: <http://tinyurl.com/pydice>')
        return 0

@bot.group(aliases=['i'])
async def init(ctx):
    """
    """
    await ctx.send("Invalid usage!")

@init.command()
async def begin(ctx, arg):
    if arg != "":
        await ctx.send("No arguments allowed!")
        return
    global cached_combat
    if cached_combat != None: # pylint: disable=used-before-assignment
        await ctx.send('Please end combat using `?i end` first!')
    else: #STARTING COMBAT
        print('Oh boy starting combat!!')
        cached_combat = Initiative()
        cached_combat.dungeon_master = ctx.author
        summary = cached_combat.get_full_text()
        await ctx.send('Your DM has begun Combat! Join by typing `?i join`')
        cached_combat.cached_summary = await ctx.send(summary)
        await cached_combat.cached_summary.pin()

@init.command()
async def end(ctx, arg):
    if arg != "":
        await ctx.send("No arguments allowed!")
        return
    global cached_combat
    if cached_combat == None:
        await ctx.send('Combat has not started!')
    else:
        if cached_combat.dungeon_master != ctx.author:
            await ctx.send('Only the DM can end combat!!')
        else: #ENDING COMBAT
            await cached_combat.cached_summary.delete()
            cached_combat = None
            await ctx.send("Combat has ended. ~~Here's to the next TPK~~ :beers:")

@init.command()
async def join(ctx, arg):
    if cached_combat == None:
        await ctx.send('Combat has not started!')
    else: # Check if player has a player!
        status, cha = cm.get_active_char(ctx.author.id)
        if status == cm.STATUS_ERR:
            await ctx.send("You haven't imported a character!")
        else:
            i = await roll_initiative(ctx, cha)
            cbt = Combatant(cha['PCName'], i, ctx.author.mention, cha['HPMax'], cha['HP'])
            print("ADDED A COMBATANT YA LATIF {0}".format(cbt))
            cached_combat.add_char(cbt)
            await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())

@init.command()
async def add(ctx, *args):
    if cached_combat == None:
        await ctx.send('Combat has not started!')
    else: 
        if cached_combat.dungeon_master != ctx.author:
            await ctx.send('Only the DM can add non player characters to combat!')
        else:
            if len(args) < 2:
                print('NOT ENOUGH OPERANDS!')
            else:
                await ctx.message.delete()
                i = await roll_initiative(ctx, None, args[1], True)
                cbt = Combatant(args[0], i,None, int(args[2]) if 0 <= 2 < len(args) else None, None, private=True)
                print("ADDED A COMBATANT YA LATIF {0}".format(cbt))
                cached_combat.add_char(cbt)
                await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())

@init.command(aliases=['hp'])
async def health(ctx, *args):
    if cached_combat == None:
        await ctx.send('Combat has not started!')
    else: 
        if cached_combat.dungeon_master != ctx.author:
            await ctx.send('Only the DM can edit NPC HP!')
        else:
            if len(args) < 2:
                print('NOT ENOUGH OPERANDS!')
            else:
                cbt = cached_combat.get_combatant_from_name(args[0])
                cbt.modify_health(int(args[1]))
                await ctx.send(cbt.get_summary())
                await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())
                await ctx.author.send(cbt.get_summary() + "Health: {}".format(cbt.current_hp))
                await ctx.message.delete()

@init.command()
async def next(ctx, *args):
    if cached_combat == None:
        await ctx.send('Combat has not started!')
    else: 
        if cached_combat.dungeon_master != ctx.author:
            await ctx.send('Only the DM can edit NPC HP!')
        else:
            current = cached_combat.next() # pylint: disable=not-callable
            await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())
            await ctx.send("{0}{1} its your turn in initiative!".format(current.mention + " " if current.mention != None else "", current.name))
                    
@bot.command()
async def hp(ctx, *args):
    status, cha = cm.get_active_char(ctx.author.id)
    if status == cm.STATUS_ERR:
        ctx.send("3mol ma3roof import a character first thanks!")
    else:
        if len(args) == 0:
            await ctx.send('{0}: {1}/{2}'.format(cha['PCName'], cha['HP'], cha['HPMax']))
        else:
            mod = int(args[0])
            cha['HP'] += mod
            if cha['HP'] < 0:
                cha['HP'] = 0
            if cha['HP'] > cha['HPMax']:
                cha['HP'] = cha['HPMax']
            db.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
            if cached_combat == None:
                await ctx.send('{0}: {1}/{2}'.format(cha['PCName'], cha['HP'], cha['HPMax']))
            else:
                cbt = cached_combat.get_combatant_from_name(cha['PCName'])
                cbt.modify_health(mod)
                await ctx.send(cbt.get_summary())
                await cached_combat.cached_summary.edit(content = cached_combat.get_full_text())

@bot.command()
async def spell(ctx, *, arg):
    await search('spell', arg, ctx)

async def search(type, arg, ctx):
    if type in SEARCH_TYPES:
        term = arg.strip()
        if type == 'spell':
            print("Searching for " + term)
            result = dm.get_spell(term)
            print("Result: ")
            print(result)
            if result != None:
                formatted_message_queue = mf.format_spell(result)
                for i in formatted_message_queue:
                    await ctx.send(embed=i)
            else:
                await ctx.send("Could not find that spell. Please spell correctly!")

    else:
        await ctx.send("That search has not been implemented yet. SORRY!")


print("Loading all saved data!")
cm.load_data()
bot.run(TOKEN)

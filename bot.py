import discord.ext.commands as commands
from d20 import RollResult
from d20 import roll as d20_roll
from pymongo import MongoClient

import main.bot_spreadsheet as bs
import main.character_manager as cm

import main.data_manager as dm
import main.helpers.reply_holder as rh

dm.init_global_data()

mongoC = MongoClient()
db = mongoC.ddb_db


class DnDBot(commands.Bot):
    def __init__(self, prefix, description=None, **options):
        super(DnDBot, self).__init__(prefix, description=description, **options)
        self.cached_combat = None
        self.database = db


bot = DnDBot('?')
cogs = ['main.cogs.initiative', 'main.cogs.character', 'main.cogs.search']


@bot.event
async def on_ready():
    bs.init()
    for cog in cogs:
        bot.load_extension(cog)
    print('Logged on as {0}'.format(bot.user))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print('Message from {0.author}: {0.content}'.format(message))

    if len(rh.replies) > 0:
        for r in rh.replies:
            await r.perform_reply(message.author.id, message.content)

    await bot.process_commands(message)


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


print("Loading all saved data!")
cm.load_data()
bot.run(dm.BOT_TOKEN)

import discord.ext.commands as commands

from d20 import RollResult, AdvType
from d20 import roll as d20_roll

import main.character_manager as cm

import main.data_manager as dm
import main.helpers.reply_holder as rh
from main.database_manager import retrieve_guild_prefix, set_guild_prefix
from main.initiative import Initiative
import sys
import math

if len(sys.argv) == 1:
    dm.init_global_data(False)
else:
    dm.init_global_data(sys.argv[1])

DEFAULT_PREFIX = '?'


class DnDBot(commands.Bot):
    """
    My custom discord bot subclass
    """
    def __init__(self, prefix, description=None, **options):
        super(DnDBot, self).__init__(prefix, description=description, **options)
        self.cached_combat = None  # type: Initiative


bot = DnDBot(lambda _, msg: retrieve_guild_prefix(msg.guild.id, DEFAULT_PREFIX))  # todo: get from Mongo
cogs = ['main.cogs.initiative', 'main.cogs.character', 'main.cogs.search']


@bot.event
async def on_ready():
    for cog in cogs:
        bot.load_extension(cog)
    print('Logged on as {0}'.format(bot.user))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # print('Message from {0.author}: {0.content}'.format(message))
    # todo: remove this idea
    if len(rh.replies) > 0:
        for r in rh.replies:
            await r.perform_reply(message.author.id, message.content)

    await bot.process_commands(message)


@bot.command(aliases=['r'])
async def roll(ctx, *, arg):
    arg = arg.split(' ')
    adv = AdvType.NONE  # 0 -> none, -1 -> dis, 1 -> adv
    try:
        term = ""
        for i in range(0, len(arg)):
            if arg[i] not in ['adv', 'dis']:
                term += arg[i]
            elif arg[i] == 'adv':
                adv = AdvType.ADV
            elif arg[i] == 'dis':
                adv = AdvType.DIS

        result = d20_roll(term, advantage=adv) if term != 'd420' else '69'

        print('Rolled {0}. Result:{1}'.format(term, str(result) if type(result) == RollResult else result))
        chatResult = 'Rolling {0} for {1}:\n'.format(term, ctx.author.mention)
        chatResult = chatResult + '{0}'.format(str(result) if type(result) == RollResult else result)
        await ctx.send(chatResult)
    except:
        await ctx.send('Invalid syntax. Check out correct syntax at: d20 library readme')


@bot.command(aliases=['py'])
async def pythagorean(ctx, *, args):
    arg = args.split(' ')

    if len(arg) < 2:
        await ctx.send('Invalid syntax.')
    else:
        result = int(arg[0])**2 + int(arg[1])**2
        result = round(math.sqrt(result),1)
        await ctx.send('Pythagorean calculation for {0}: {1}'.format(ctx.author.mention, result))


@bot.command()
async def prefix(ctx, *args):
    if len(args) < 1:
        await ctx.send('Current server prefix is {0}'.format(retrieve_guild_prefix(ctx.guild.id, DEFAULT_PREFIX)))
    elif len(args) > 1:
        await ctx.send('The prefix cannot contain a space. Please try again!')
    else:
        set_guild_prefix(ctx.guild.id, args[0])
        await ctx.send('Current server prefix is now {0}'.format(retrieve_guild_prefix(ctx.guild.id, DEFAULT_PREFIX)))


print("Loading all saved data!")
cm.load_data()
bot.run(dm.BOT_TOKEN)
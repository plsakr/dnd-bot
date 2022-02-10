import discord
import discord.ext.commands as commands

from d20 import RollResult, AdvType
from d20 import roll as d20_roll
from discord import SlashCommand, ApplicationContext, DiscordException
from discord.commands import permissions
from main.helpers.mongo_handler import MongoHandler

import main.character_manager as cm

import main.data_manager as dm
import sys
import traceback

if len(sys.argv) == 1:
    mongo_db = dm.init_global_data(False)
else:
    mongo_db = dm.init_global_data(sys.argv[1])

from main.database_manager import retrieve_guild_prefix, set_guild_prefix

import math

from main.cogs import search, initiative, character
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
handler = MongoHandler(mongo_db, level=logging.DEBUG)
logger.addHandler(handler)

DEFAULT_PREFIX = '?'


class DnDBot(commands.Bot):
    """
    My custom discord bot subclass. Note that prefix no longer is used by any current commands, however
    it will remain in the code for any possible future needs.
    """

    def __init__(self, prefix, description=None, **options):
        super(DnDBot, self).__init__(prefix, description=description, activity=discord.Game(name='Backseat DM'),
                                     **options)

    def slash_command(self, **kwargs):
        if dm.TEST_GUILD_ID > 0:
            return self.application_command(cls=SlashCommand, guild_ids=[dm.TEST_GUILD_ID], **kwargs)
        else:
            return self.application_command(cls=SlashCommand, **kwargs)

    async def on_application_command_error(self, context: ApplicationContext, exception: DiscordException) -> None:
        print('Error encountered. Logging')
        tb = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        logger.error(f'Exception encountered in command {context.command} with message: {exception}.\nTraceback:{tb}')


def get_command_prefix(msg):
    if msg.guild is None:
        return ''
    return retrieve_guild_prefix(msg.guild.id, DEFAULT_PREFIX)


bot = DnDBot(lambda _, msg: get_command_prefix(msg), owner_id=dm.OWNER_ID,
             debug_guilds=([dm.TEST_GUILD_ID] if dm.TEST_GUILD_ID != -1 else None))

bot.add_cog(search.Search(bot))
bot.add_cog(initiative.Init(bot))
bot.add_cog(character.Character(bot))


@bot.event
async def on_ready():
    print('Logged on as {0}'.format(bot.user))


@bot.slash_command()
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
        await ctx.respond(chatResult)
    except:
        await ctx.respond('Invalid syntax. Check out correct syntax at: d20 library readme')


@bot.slash_command()
async def rstats(ctx):
    await ctx.respond('Rolling Character Stats:')
    for i in range(0, 6):
        await roll(ctx, arg="4d6rr1kh3")


@bot.slash_command()
async def pythagorean(ctx, *, args):
    arg = args.split(' ')

    if len(arg) < 2:
        await ctx.respond('Invalid syntax.')
    else:
        result = int(arg[0]) ** 2 + int(arg[1]) ** 2
        result = round(math.sqrt(result), 1)
        await ctx.respond('Pythagorean calculation for {0}: {1}'.format(ctx.author.mention, result))


@bot.command()
async def prefix(ctx, *args):
    if len(args) < 1:
        await ctx.send('Current server prefix is {0}'.format(retrieve_guild_prefix(ctx.guild.id, DEFAULT_PREFIX)))
    elif len(args) > 1:
        await ctx.send('The prefix cannot contain a space. Please try again!')
    else:
        set_guild_prefix(ctx.guild.id, args[0])
        await ctx.send('Current server prefix is now {0}'.format(retrieve_guild_prefix(ctx.guild.id, DEFAULT_PREFIX)))


@bot.slash_command()
@permissions.is_owner()
async def crash_bot(ctx):
    raise Exception("Test Exception!")


print("Loading all saved data!")
cm.load_data()
bot.run(dm.BOT_TOKEN)

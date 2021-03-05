import discord.ext.commands as commands
from d20 import RollResult, AdvType
from d20 import roll as d20_roll

import main.character_manager as cm

import main.data_manager as dm
import main.helpers.reply_holder as rh
from main.initiative import Initiative
import sys

if len(sys.argv) == 1:
    dm.init_global_data(False)
else:
    dm.init_global_data(sys.argv[1])


class DnDBot(commands.Bot):
    def __init__(self, prefix, description=None, **options):
        super(DnDBot, self).__init__(prefix, description=description, **options)
        self.cached_combat = None  # type: Initiative


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

    # print('Message from {0.author}: {0.content}'.format(message))
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


print("Loading all saved data!")
cm.load_data()
bot.run(dm.BOT_TOKEN)
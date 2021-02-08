from discord.ext import commands
from discord import channel
from main.initiative import Initiative, Combatant
from d20 import roll as d20_roll

import main.character_manager as cm


class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['i'])
    async def init(self, ctx):
        """
        """
        # await ctx.send("Invalid usage!")

        if ctx.invoked_subcommand is not None:
            return

        if self.bot.cached_combat is not None:
            summary = self.bot.cached_combat.get_full_text()
            await ctx.send(summary)

    @init.command()
    async def begin(self, ctx):
        if self.bot.cached_combat is not None:
            await ctx.send('Please end combat using `?i end` first!')
        else:  # STARTING COMBAT
            print('Oh boy starting combat!!')
            self.bot.cached_combat = Initiative()
            self.bot.cached_combat.dungeon_master = ctx.author
            summary = self.bot.cached_combat.get_full_text()
            await ctx.send('Your DM has begun Combat! Join by typing `?i join`')
            self.bot.cached_combat.cached_summary = await ctx.send(summary)
            await self.bot.cached_combat.cached_summary.pin()

    @init.command()
    async def end(self, ctx):
        if self.bot.cached_combat is None:
            await ctx.send('Combat has not started!')
        else:
            if self.bot.cached_combat.dungeon_master != ctx.author:
                await ctx.send('Only the DM can end combat!!')
            else:  # ENDING COMBAT
                await self.bot.cached_combat.cached_summary.delete()
                self.bot.cached_combat = None
                await ctx.send("Combat has ended. ~~Here's to the next TPK~~ :beers:")

    @init.command()
    async def join(self, ctx):
        if self.bot.cached_combat is None:
            await ctx.send('Combat has not started!')
        else:  # Check if player has a player!
            status, cha = cm.get_active_char(ctx.author.id)
            if status == cm.STATUS_ERR:
                await ctx.send("You haven't imported a character!")
            else:
                i = await roll_initiative(ctx, cha)
                cbt = Combatant(cha['name'], i, ctx.author.mention, cha['HPMax'], cha['HP'])
                print("ADDED A COMBATANT YA LATIF {0}".format(cbt))
                self.bot.cached_combat.add_char(cbt)
                await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())

    @init.command()
    async def add(self, ctx, *args):
        if self.bot.cached_combat is None:
            await ctx.send('Combat has not started!')
        else:
            if self.bot.cached_combat.dungeon_master != ctx.author:
                await ctx.send('Only the DM can add non player characters to combat!')
            else:
                if len(args) < 2:
                    print('NOT ENOUGH OPERANDS!')
                else:
                    if not isinstance(ctx.channel, channel.DMChannel):
                        await ctx.message.delete()
                    i = await roll_initiative(ctx, None, args[1], True)
                    cbt = Combatant(args[0], i, None, int(args[2]) if 0 <= 2 < len(args) else None, None, private=True)
                    print("ADDED A COMBATANT YA LATIF {0}".format(cbt))
                    self.bot.cached_combat.add_char(cbt)
                    await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())

    @init.command(aliases=['r'])
    async def remove(self, ctx, arg):
        if self.bot.cached_combat is None:
            await ctx.send('Combat has not started!!')
        else:
            if self.bot.cached_combat.dungeon_master != ctx.author:
                await ctx.send('Only the DM can add non player characters to combat!')
            else:
                await ctx.message.delete()

                if self.bot.cached_combat.check_char_exists(arg):

                    # if it is their turn, DO NOT ALLOW REMOVAL!
                    combatant = self.bot.cached_combat.get_combatant_from_name(arg)
                    if combatant.current_turn:
                        await ctx.send('Cannot remove combatant on their turn!')
                    else:
                        self.bot.cached_combat.remove_char(arg)
                        await ctx.send('Removed {0} from initiative'.format(arg))
                else:
                    await ctx.send('Could not find that combatant in initiative. Please type the whole name (if spaces use "")')
                await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())

    @init.command(aliases=['hp'])
    async def health(self, ctx, *args):
        if self.bot.cached_combat is None:
            await ctx.send('Combat has not started!')
        else:
            if self.bot.cached_combat.dungeon_master != ctx.author:
                await ctx.send('Only the DM can edit NPC HP!')
            else:
                if len(args) < 2:
                    print('NOT ENOUGH OPERANDS!')
                else:
                    cbt = self.bot.cached_combat.get_combatant_from_name(args[0])
                    cbt.modify_health(int(args[1]))
                    await ctx.send(cbt.get_summary())
                    await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())
                    await ctx.author.send(cbt.get_summary() + "Health: {}".format(cbt.current_hp))
                    await ctx.message.delete()

    @init.command()
    async def next(self, ctx):
        if self.bot.cached_combat is None:
            await ctx.send('Combat has not started!')
        else:
            if self.bot.cached_combat.dungeon_master != ctx.author:
                await ctx.send('Only the DM can use that command!')
            else:
                current = self.bot.cached_combat.next()  # pylint: disable=not-callable
                await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())
                await ctx.send("{0}{1} its your turn in initiative!".format(
                    current.mention + " " if current.mention is not None else "", current.name))


async def roll_initiative(ctx, cha=None, initBonus=None, private=False):
    try:
        result = d20_roll("1d20+{0}".format(cha['init'] if cha != None else initBonus))
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


def setup(bot):
    bot.add_cog(Init(bot))
    print("Added Initiative Cog!")

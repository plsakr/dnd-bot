from types import SimpleNamespace

from discord.ext import commands
from discord import channel, NotFound
from discord.commands import Option

from main.initiative import Initiative, Combatant
from d20 import roll as d20_roll
from main.cogs.search import search
from math import floor

import main.character_manager as cm
import main.data_manager as dm
from main.command_groups import init


def obj_to_dict(obj):
    if type(obj) is dict:
        res = {}
        for k, v in obj.items():
            res[k] = obj_to_dict(v)
        return res
    elif type(obj) is list:
        return [obj_to_dict(item) for item in obj]
    elif type(obj) in [Initiative, Combatant]:
        return obj_to_dict(vars(obj))
    else:
        return obj


async def save_combat(ctx, cbt):
    combat_obj = obj_to_dict(cbt) if cbt is not None else None
    dm.save_cached_combat(ctx.guild.id, ctx.channel.id, combat_obj)


async def get_cached_combat(ctx):
    return dm.get_cached_combat(ctx.guild.id, ctx.channel.id)


class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # type: DnDBot

    @init.command(guild_ids=[608192441333317683])
    async def info(self, ctx):
        """
        """
        # await ctx.send("Invalid usage!")

        cbt = await get_cached_combat(ctx)
        if cbt is not None:
            summary = cbt.get_full_text()
            await ctx.respond(summary)

    @init.command(guild_ids=[608192441333317683])
    async def begin(self, ctx):
        if (await get_cached_combat(ctx)) is not None:
            await ctx.respond('Please end combat using `?i end` first!', ephemeral=True)
        else:  # STARTING COMBAT
            print('Oh boy starting combat!!')
            cached_combat = Initiative()
            cached_combat.dungeon_master = ctx.author.id
            summary = cached_combat.get_full_text()
            await ctx.respond('Starting combat on this channel! Good luck DM!', ephemeral=True)
            await ctx.send('Your DM has begun Combat! Join by typing `?i join`')
            message = await ctx.send(summary)
            cached_combat.cached_summary = message.id
            await save_combat(ctx, cached_combat)
            await message.pin()

    @init.command(guild_ids=[608192441333317683])
    async def end(self, ctx):
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can end combat!!', ephemeral=True)
            else:  # ENDING COMBAT
                try:
                    msg = await ctx.fetch_message(combat.cached_summary)
                    await msg.delete()
                except NotFound:
                    print('could not delete combat message')
                await save_combat(ctx, None)
                await ctx.respond("Combat has ended. ~~Here's to the next TPK~~ :beers:")

    @init.command(guild_ids=[608192441333317683])
    async def join(self, ctx):
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:  # Check if player has a player!
            status, cha = cm.get_active_char(ctx.author.id)
            if status == cm.STATUS_ERR:
                await ctx.respond("You haven't imported a character!", ephemeral=True)
            else:
                i = await roll_initiative(ctx, cha)
                cbt = Combatant(cha['name'], i, True, ctx.author.mention, cha['HPMax'], cha['HP'])
                combat.add_char(cbt)
                msg = await ctx.fetch_message(combat.cached_summary)
                if msg is not None:
                    await msg.edit(combat.get_full_text())
                await save_combat(ctx, combat)

    @init.command(guild_ids=[608192441333317683])
    async def add(self, ctx, name: Option(str, "Name of combatant"),
                  init_bonus: Option(int, "Initiative bonus / value"),
                  set_init: Option(bool, "Set initiative directly?", required=False, default=False),
                  hp: Option(int, "Combatant HP", required=False, default=0)):
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.send('Combat has not started!', ephemeral=True)
        else:

            if set_init is not None and set_init:
                i = init_bonus
                ctx.respond('Added combatant at specific initiative!', ephemeral=True)
            else:
                i = await roll_initiative(ctx, None, init_bonus, True)

            cbt = Combatant(name, i, False, None, hp if hp != 0 else None, None,
                            private=True)
            print("ADDED A COMBATANT {0}".format(cbt))

            combat.add_char(cbt)
            await save_combat(ctx, combat)
            try:
                message = await ctx.fetch_message(combat.cached_summary)
                await message.edit(combat.get_full_text())
            except NotFound:
                print('could not find message!')

    @init.command(guild_ids=[608192441333317683])
    async def madd(self, ctx, name: Option(str, "Monster name"), custom_hp: Option(int, "Custom hp", required=False, default=0)):
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can add monsters to combat!', ephemeral=True)
            else:
                async def on_monster_found(monster):
                    if monster is not None:
                        i = await roll_initiative(ctx, None, floor((monster['dex'] - 10) / 2), True)

                    first_name = monster['name'].upper()
                    if len(first_name) > 3:
                        first_name = first_name[0:2]
                    name = combat.get_next_name(first_name)
                    if custom_hp is None or custom_hp == 0:
                        # search for monster, add as is

                        cbt = Combatant(name, i, False, None, monster['hp']['average'], None,
                                        private=True)
                    else:
                        # search for monster, add it with custom hp
                        cbt = Combatant(name, i, False, None, custom_hp, None,
                                        private=True)
                    combat.add_char(cbt)
                    await save_combat(ctx, combat)
                    try:
                        message = await ctx.fetch_message(combat.cached_summary)
                        await message.edit(combat.get_full_text())
                    except NotFound:
                        print('could not find message!')

                async def on_find_monster_i(_, monster):
                    await on_monster_found(monster)

                await search('monster', name, ctx, on_monster_found, on_find_monster_i)

    @init.command(guild_ids=[608192441333317683])
    async def remove_combatant(self, ctx, name: Option(str, 'Name of combatant to remove')):
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can remove monsters from combat!', ephemeral=True)
            else:
                await ctx.message.delete()

                result = self.bot.cached_combat.attempt_char_removal(name)
                if result != -2:
                    # if it is their turn, DO NOT ALLOW REMOVAL!
                    if result == -1:
                        await ctx.respond('Cannot remove combatant on their turn!', ephemeral=True)
                    else:
                        await ctx.respond('Removed {0} from initiative'.format(name))
                else:
                    await ctx.respond('Could not find that combatant in initiative. Please type the whole name', ephemeral=True)
                await save_combat(ctx, combat)
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')

    # TODO: migrate to slash!
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

    @init.command(guild_ids=[608192441333317683])
    async def next(self, ctx):
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can use that command!', ephemeral=True)
            else:
                current = combat.next()
                to_remove = []

                # check for dead people
                while current.current_hp is not None and current.current_hp <= 0 and not current.is_player:
                    print('I see dead people!')
                    await ctx.send('{0} is dead. Skipping their turn!'.format(current.name))
                    to_remove.append(current.name)
                    current = self.bot.cached_combat.next()

                if len(to_remove) > 0:
                    await ctx.send('Removing {0} dead combatants!'.format(len(to_remove)))
                    [self.bot.cached_combat.attempt_char_removal(i) for i in to_remove]
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')

                await save_combat(ctx, combat)
                await ctx.respond("{0}{1} its your turn in initiative!".format(
                    current.mention + " " if current.mention is not None else "", current.name))


async def roll_initiative(ctx, cha=None, initBonus=None, private=False):
    try:
        result = d20_roll("1d20+{0}".format(cha['init'] if cha is not None else initBonus))
        print('Rolled for initiative. Result:{0}'.format(result.total))
        chatResult = '{0} Rolling for Initiative:\n'.format(ctx.author.mention) if not private else 'Secretly Rolling for Initiative:\n'
        chatResult = chatResult + '{0}'.format(str(result))
        if private == False:
            await ctx.respond(chatResult)
        else:
            await ctx.respond(chatResult, ephemeral=True)
        return result.total
    except:
        await ctx.respond('Invalid syntax.', ephemeral=True)
        return 0


def setup(bot):
    bot.add_cog(Init(bot))
    print("Added Initiative Cog!")

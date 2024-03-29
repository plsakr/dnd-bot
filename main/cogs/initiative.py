import discord
from discord.ext import commands
from discord import NotFound, SlashCommandGroup
from discord.commands import Option

from main.helpers.combat_helper import get_cached_combat, save_combat
from main.initiative import Initiative, Combatant
from d20 import roll as d20_roll
from main.cogs.search import search
from math import floor

import main.character_manager as cm
import main.data_manager as dm


async def autocomplete_combatants(ctx: discord.AutocompleteContext):
    print(type(ctx.interaction))
    combat = dm.get_cached_combat(ctx.interaction.guild_id, ctx.interaction.channel_id)
    if combat is None:
        return []
    return [x.name for x in combat.players if x.name.lower().startswith(ctx.value.strip().lower())]


async def autocomplete_npc_combatants(ctx: discord.AutocompleteContext):
    combat = dm.get_cached_combat(ctx.interaction.guild_id, ctx.interaction.channel_id)
    if combat is None:
        return []
    return [x.name for x in combat.players if x.name.lower().startswith(ctx.value.strip().lower()) and x.mention is None]


class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # type: DnDBot

    initiative = SlashCommandGroup("i", "Various commands for initiative!")

    @initiative.command()
    async def info(self, ctx):
        """Prints the status of the current combat."""
        cbt = await get_cached_combat(ctx)
        if cbt is not None:
            await ctx.respond("_Note: The following data will not be updated._\n" + cbt.get_full_text(), ephemeral=True)
        else:
            await ctx.respond("Combat has not started yet", ephemeral=True)

    @initiative.command()
    async def begin(self, ctx):
        """Begin a new combat in this channel."""
        if (await get_cached_combat(ctx)) is not None:
            await ctx.respond('Please end combat using `/i end` first!', ephemeral=True)
        else:  # STARTING COMBAT
            print('Oh boy starting combat!!')
            cached_combat = Initiative()
            cached_combat.dungeon_master = ctx.author.id
            summary = cached_combat.get_full_text()
            await ctx.respond('Starting combat on this channel! Good luck DM!', ephemeral=True)
            await ctx.send('Your DM has begun Combat! Join by typing `/join`')
            message = await ctx.send(summary)
            cached_combat.cached_summary = message.id
            await save_combat(ctx, cached_combat)
            await message.pin()

    @initiative.command()
    async def end(self, ctx):
        """End the currently active combat."""
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

    @initiative.command()
    async def join(self, ctx):
        """Join the active combat with your currently selected character."""
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:  # Check if player has a player!
            status, cha = cm.get_active_char(ctx.author.id)
            if status == cm.STATUS_ERR:
                await ctx.respond("You haven't imported a character!", ephemeral=True)
            else:
                if not combat.check_char_exists(cha['name']):
                    i = await roll_initiative(ctx, cha)
                    cbt = Combatant(cha['name'], i, True, ctx.author.mention, cha['HPMax'], cha['HP'])
                    combat.add_char(cbt)
                    msg = await ctx.fetch_message(combat.cached_summary)
                    if msg is not None:
                        await msg.edit(combat.get_full_text())
                    await save_combat(ctx, combat)
                else:
                    await ctx.respond("You already joined this combat!", ephemeral=True)

    @initiative.command()
    async def add(self, ctx, name: Option(str, "Name of combatant"),
                  init_bonus: Option(int, "Initiative bonus / value"),
                  set_init: Option(bool, "Set initiative directly?", required=False, default=False),
                  hp: Option(int, "Combatant HP", required=False, default=0)):
        """Add a custom combatant to the initiative."""
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.send('Combat has not started!', ephemeral=True)
        else:

            if name.strip() not in [x.name for x in combat.players]:
                if set_init is not None and set_init:
                    i = init_bonus
                    ctx.respond('Added combatant at specific initiative!', ephemeral=True)
                else:
                    i = await roll_initiative(ctx, None, init_bonus, True)

                cbt = Combatant(name, i, True, None, hp if hp != 0 else None, None,
                                private=True)
                print("ADDED A COMBATANT {0}".format(cbt))

                combat.add_char(cbt)
                await save_combat(ctx, combat)
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')
            else:
                await ctx.respond('That name already exists in initiative! Please change the name and try again', ephemeral=True)

    @initiative.command()
    async def madd(self, ctx, name: Option(str, "Monster name"), custom_hp: Option(int, "Custom hp", required=False, default=0)):
        """Add a monster using its stats to the initiative."""
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

    @initiative.command()
    async def remove_combatant(self, ctx, name: Option(str, 'Name of combatant to remove',
                                                       autocomplete=autocomplete_combatants)):
        """Remove a combatant from initiative."""
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can remove monsters from combat!', ephemeral=True)
            else:

                result = combat.attempt_char_removal(name)
                if result != -2:
                    # if it is their turn, DO NOT ALLOW REMOVAL!
                    if result == -1:
                        await ctx.respond('Cannot remove combatant on their turn!', ephemeral=True)
                    else:
                        await ctx.respond('Removed {0} from initiative'.format(name))
                else:
                    await ctx.respond('Could not find that combatant in initiative. Please type the whole name',
                                      ephemeral=True)
                await save_combat(ctx, combat)
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')

    @initiative.command()
    async def hp(self, ctx, combatant: Option(str, "name of combatant", autocomplete=autocomplete_npc_combatants),
                     modifier: Option(int, "health modifier")):
        """Edit a combatant's hp (non-character)"""
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can edit NPC hp!', ephemeral=True)
            else:
                cbt = combat.get_combatant_from_name(combatant)
                cbt.modify_health(modifier)
                await ctx.respond(cbt.get_summary())
                await save_combat(ctx, combat)
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')
                await ctx.author.send(cbt.get_summary() + "Health: {}".format(cbt.current_hp))

    @initiative.command()
    async def next(self, ctx):
        """Begin combat or move to the next combatant in initiative."""
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can use that command!', ephemeral=True)
            else:
                await ctx.defer()
                current = combat.next()
                to_remove = []

                # check for dead people
                while current.current_hp is not None and current.current_hp <= 0 and not current.is_player:
                    print('I see dead people!')
                    await ctx.send('{0} is dead. Skipping their turn!'.format(current.name))
                    to_remove.append(current.name)
                    current = combat.next()

                if len(to_remove) > 0:
                    await ctx.send('Removing {0} dead combatants!'.format(len(to_remove)))
                    [combat.attempt_char_removal(i) for i in to_remove]
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')

                await save_combat(ctx, combat)

                if len(combat.players) == 0 or combat.all_players_dead(): # all player combatants dead. send TPK message and end combat!
                    await ctx.respond('Well Done DM! You got everyone killed. TPK Accomplished!')
                    try:
                        msg = await ctx.fetch_message(combat.cached_summary)
                        await msg.delete()
                    except NotFound:
                        print('could not delete combat message')
                    await save_combat(ctx, None)
                    return

                await ctx.respond("{0}{1} its your turn in initiative!".format(
                    current.mention + " " if current.mention is not None else "", current.name))

    @initiative.command()
    async def edit_initiative(self, ctx,
                              combatant: Option(str, "name of combatant", autocomplete=autocomplete_combatants),
                              new_initiative: Option(int, "New Initiative Value")):
        """Edit a combatant's initiative value"""
        combat = await get_cached_combat(ctx)
        if combat is None:
            await ctx.respond('Combat has not started!', ephemeral=True)
        else:
            if combat.dungeon_master != ctx.author.id:
                await ctx.respond('Only the DM can use that command!', ephemeral=True)
            else:
                await ctx.defer()
                cbt = combat.get_combatant_from_name(combatant)
                cbt.init = new_initiative
                combat.sort_initiative()
                await save_combat(ctx, combat)
                try:
                    message = await ctx.fetch_message(combat.cached_summary)
                    await message.edit(combat.get_full_text())
                except NotFound:
                    print('could not find message!')
                await ctx.respond('Initiative value edited successfully.', ephemeral=True)


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

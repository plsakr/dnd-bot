from discord.ext import commands
from discord.commands import slash_command, Option
import main.data_manager as dm
import main.message_formatter as mf
from main.helpers.annotations import my_slash_command

SEARCH_TYPES = ['spell', 'monster']


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @my_slash_command()
    async def spell(self, ctx, term: Option(str, "Enter search term")):
        async def on_find(spell):
            message_queue = mf.format_spell(ctx, spell)
            await ctx.respond(embeds=message_queue)

        async def on_find_interaction(interaction, spell):
            if spell is not None:
                message_queue = mf.format_spell(ctx, spell)
                await interaction.response.send_message(embeds=message_queue)

        await ctx.defer()
        await search('spell', term, ctx, on_find, on_find_interaction)

    @my_slash_command()
    async def item(self, ctx, term: Option(str, "Enter search term")):
        await ctx.defer()
        await search('item', term, ctx)

    @my_slash_command()
    async def monster(self, ctx, term: Option(str, "Enter search term")):
        async def on_find(monster):
            message_queue = mf.format_monster(ctx, monster)
            await ctx.respond(embeds=message_queue)

        async def on_find_interaction(interaction, monster):
            if monster is not None:
                message_queue = mf.format_monster(ctx, monster)
                await interaction.response.send_message(embeds=message_queue)

        await ctx.defer()
        await search('monster', term, ctx, on_find, on_find_interaction)


async def search(search_type, arg, ctx, on_find, on_find_interaction):
    if search_type in SEARCH_TYPES:
        term = arg.strip()
        if search_type == 'spell':
            print("Searching for " + term)
            monster_choices, names = dm.get_spell_choices(dm.create_grams(term.lower()))
            if len(monster_choices) == 0:
                await ctx.respond("Could not find any spells with those search terms.")
            else:
                if monster_choices[0]['score'] == 1.0:
                    print('found a spell with 100% match, sending directly')
                    spell = dm.get_spell_by_id(monster_choices[0]['ref'])
                    await on_find(spell)
                else:
                    # there are more than one option. Print them out, and ask the user for a number
                    async def on_choose(i, interaction):
                        if i < len(monster_choices):
                            spell = dm.get_spell_by_id(monster_choices[i]['ref'])
                            await on_find_interaction(interaction, spell)
                        else:
                            await interaction.response.edit_message(content='Search cancelled', view=None)
                            await on_find_interaction(interaction, None)

                    my_view = mf.DropdownView(names, on_choose)
                    await ctx.respond('Found multiple choices:', view=my_view, ephemeral=True)

        elif search_type == 'monster':
            print("Searching for " + term)
            monster_choices, names = dm.get_monster_choices(dm.create_grams(term.lower()))
            if len(monster_choices) == 0:
                await ctx.respond("Could not find any monsters with those search terms. Are you that illiterate?")
            else:
                if monster_choices[0]['score'] == 1.0:
                    print('found a monster with 100% match, sending directly')
                    monster = dm.get_monster_by_id(monster_choices[0]['ref'])
                    await on_find(monster)
                else:
                    #there are more than one option. Print them out, and ask the user for a number
                    async def on_choose(i, interaction):
                        if i < len(monster_choices):
                            monster = dm.get_monster_by_id(monster_choices[i]['ref'])
                            await on_find_interaction(interaction, monster)
                        else:
                            await interaction.response.edit_message(content='Search cancelled', view=None)
                            await on_find_interaction(interaction, None)

                    my_view = mf.DropdownView(names, on_choose)
                    await ctx.respond('Found multiple choices:', view=my_view, ephemeral=True)
    else:
        await ctx.respond("That search has not been implemented yet. SORRY!", ephemeral=True)


def setup(bot):
    bot.add_cog(Search(bot))
    print("Added Search Cog!")
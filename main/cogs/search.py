from discord.ext import commands
import main.data_manager as dm
import main.message_formatter as mf

SEARCH_TYPES = ['spell', 'monster']


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spell(self, ctx, *, arg):
        await search('spell', arg, ctx)

    @commands.command()
    async def item(self, ctx, *, arg):
        await search('item', arg, ctx)

    @commands.command()
    async def monster(self, ctx, *, arg):
        await search('monster', arg, ctx)


async def search(search_type, arg, ctx):
    if search_type in SEARCH_TYPES:
        term = arg.strip()
        if search_type == 'spell':
            print("Searching for " + term)
            result = dm.get_spell(term)
            print("Result: ")
            print(result)
            if result is not None:
                formatted_message_queue = mf.format_spell(result)
                for i in formatted_message_queue:
                    await ctx.send(embed=i)
            else:
                await ctx.send("Could not find that spell. Please spell correctly!")
        elif search_type == 'monster':
            print("Searching for " + term)
            result = dm.get_monster(term)
            print("Result: ")
            if result is not None:
                message_queue = mf.format_monster(ctx, result)
                for i in message_queue:
                    await ctx.send(embed=i)
            else:
                await ctx.send("Could not find that monster. Please spell correctly!")

    else:
        await ctx.send("That search has not been implemented yet. SORRY!")


def setup(bot):
    bot.add_cog(Search(bot))
    print("Added Search Cog!")
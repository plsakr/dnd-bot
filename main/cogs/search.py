from discord.ext import commands
import main.data_manager as dm
import main.message_formatter as mf
import main.helpers.reply_holder as rh

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
            monster_choices, names = dm.get_monster_choices(create_grams(term.lower()))
            if len(monster_choices) == 0:
                await ctx.send("Could not find any monsters with those search terms. Are you that illiterate?")
            else:
                if monster_choices[0]['score'] == 1.0:
                    print('found a monster with 100% match, sending directly')
                    monster = dm.get_monster_by_id(monster_choices[0]['ref'])
                    message_queue = mf.format_monster(ctx, monster)
                    for i in message_queue:
                        await ctx.send(embed=i)
                else:
                    #there are more than one option. Print them out, and ask the user for a number
                    prompt = mf.format_monster_choices(names, ctx.author)
                    await ctx.send(prompt)

                    async def on_reply(reply):
                        if reply.lower() == 'c':
                            await ctx.send('Search canceled.')
                        else:
                            try:
                                index = int(reply) - 1
                                if index < len(monster_choices):
                                    monster = dm.get_monster_by_id(monster_choices[index]['ref'])
                                    message_queue = mf.format_monster(ctx, monster)
                                    for i in message_queue:
                                        await ctx.send(embed=i)
                                else:
                                    await ctx.send('Does that number look like it would work??')
                            except ValueError:
                                await ctx.send("Please input a number. Switching Canceled. Use `?switch` again")

                    holder = rh.ReplyHolder(ctx.author.id, on_reply)
                    rh.replies.append(holder)


    else:
        await ctx.send("That search has not been implemented yet. SORRY!")


def create_grams(query: str, n=3):
    actual = query.lower()
    words = actual.split(" ")
    out = []
    for w in words:
        length = len(w)
        for i in range(0, length, n):
            out.append(w[i:i+n])

    return out


def setup(bot):
    bot.add_cog(Search(bot))
    print("Added Search Cog!")
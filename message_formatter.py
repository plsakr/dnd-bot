import discord

def format_spell(search_result):
    search = search_result["value"]

    embed = None
    if '#N/A' in search:
        embed = discord.Embed(title=search[0], description="I'm sorry but everyone was too lazy to add spell data to the database")
    else:
        desc = ""
        if search[2] == '0':
            desc += "cantrip "
        else:
            desc += search[2] + " "
        desc += search[3]

        embed = discord.Embed(title=search[0], description=desc, color=0xff0000)
        embed.add_field(name="Casting time", value=search[4], inline=True)
        embed.add_field(name="Range", value=search[6], inline=True)
        embed.add_field(name="Components", value=search[7], inline=True)
        embed.add_field(name="Duration", value=search[5], inline=True)
        embed.add_field(name="Description", value=search[8], inline=False)

        footer = "Reference: " + search[9]
        embed.set_footer(text=footer)
    return embed
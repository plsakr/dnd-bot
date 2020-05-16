import discord

def format_spell(search_result):
    search = search_result

    embed = []
    if search["level"] == "#N/A":
        embed.append(discord.Embed(title=search["_id"], description="I'm sorry but everyone was too lazy to add spell data to the database"))
    else:
        name = search['_id']
        level = search['level']
        school = search['school']
        cast_time = search['cast_time']
        is_ritual = search['is_ritual']
        duration = search['duration']
        rng = search['rng']
        components = search['components']
        description = search['description']
        ref = search['ref']
        desc = ""
        if level == '0':
            desc += school + " cantrip "
        else:
            desc += "level " + level + " " + school

        color = 0xffffff

        if school == "Enchantment":
            color = 0x00ff00
        elif school == "Conjuration":
            color = 0xf6ff00
        elif school == "Divination":
            color = 0x00fffb
        elif school == "Necromancy":
            color = 0x09ff00
        elif school == "Evocation":
            color = 0xff0000
        elif school == "Abjuration":
            color = 0xff8c00
        elif school == "Transmutation":
            color = 0x00ffb7

        if is_ritual == "Yes":
            cast_time += " (ritual)"


        embed.append(discord.Embed(title=name, description=desc, color=color))
        embed[0].add_field(name="Casting time", value=cast_time, inline=True)
        embed[0].add_field(name="Range", value=rng, inline=True)
        embed[0].add_field(name="Components", value=components, inline=True)
        embed[0].add_field(name="Duration", value=duration, inline=True)

        if len(description) < 1020:
            embed[0].add_field(name="Description", value=description, inline=False)
        else:
            pieces = [description[:1020]] + [description[i:i + 2040] for i in range(1020, len(description), 2040)]
            embed[0].add_field(name="Description", value=pieces[0], inline=False)
            for piece in pieces[1:]:
                temp_embed = discord.Embed()
                temp_embed.colour = color
                temp_embed.description = piece
                embed.append(temp_embed)

        footer = "Reference: " + ref
        embed[len(embed)-1].set_footer(text=footer)
    return embed
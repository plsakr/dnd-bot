import discord
from math import floor
import random
import re



def format_characters(character_list, author, active_id, choosing=False):
    output = ""
    if not choosing:
        output = "{0}'s imported characters:\n".format(author.mention)
    else:
        output = "{0} Reply with a number to switch characters:\n".format(author.mention)
    index = 1

    for char in character_list:
        output += "{0}. {1}\t{2}\n".format(index, char['name'], ":white_check_mark:" if char['id'] == active_id else "")
        index += 1

    return output


def format_monster_choices(name_list, author):
    output = "{0} I found multiple matches. Please type the number that matches your result:\n".format(author.mention)
    index = 1
    for n in name_list:
        output += "{0}. {1}\n".format(index, n)
        index += 1
    output += "Or, send c to cancel search."
    return output


def reformat_dice(inString):
    pattern = '{([^}]*)}'
    current = inString
    match = re.search(pattern, current)
    index = 0
    while match is not None and index < 30:
        index += 1
        start, end = match.span()
        value = match.group()
        value = value[1:]
        value = value[:-1]

        command = value.split(' ')[0]
        if command == '@h':
            current = current[0:start:] + current[end::]
        elif command == '@atk':
            subs = value.split(' ')[1]
            if subs == 'mw':
                current = current[0:start:] + '_Melee Weapon Attack:_' + current[end::]
            elif subs == 'rw':
                current = current[0:start:] + '_Ranged Weapon Attack:_' + current[end::]
            else:
                current = current[0:start:] + '_Melee or Ranged Weapon Attack:_' + current[end::]
        elif command == '@hit':
            current = current[0:start:] + '+' + value.split(' ')[1] + current[end::]
        elif command == '@damage':
            current = current[0:start:] + value.split(' ', 1)[1] + current[end::]
        elif command == '@chance':
            current = current[0:start:] + value.split('|')[-1] + current[end::]
        elif command == '@dc':
            current = current[0:start:] + '**' + value.split(' ')[1] + '**' + current[end::]
        elif command == '@condition':
            current = current[0:start:] + '_' + value.split(' ')[1] + '_' + current[end::]
        elif command == '@spell':
            current = current[0:start:] + '**' + value.split(' ', 1)[1] + '**' + current[end::]
        elif command == '@dice':
            current = current[0:start:] + value.split(' ', 1)[1] + current[end::]
        match = re.search(pattern, current)

    return current


def format_spell(ctx, spell):

    def format_spell_school(school):
        if school == 'A':
            return 'Abjuration'
        elif school == 'C':
            return 'Conjuration'
        elif school == 'D':
            return 'Divination'
        elif school == 'E':
            return 'Enchantment'
        elif school == 'I':
            return 'Illusion'
        elif school == 'N':
            return 'Necromancy'
        elif school == 'T':
            return 'Transmutation'
        elif school == 'V':
            return 'Evocation'

    def format_spell_duration(duration_obj):
        out = ''
        if duration_obj['type'] == 'timed':
            out += '{0} {1}'.format(duration_obj['duration']['amount'], duration_obj['duration']['type'])
            if 'concentration' in duration_obj:
                out += ' (Concentration)'
        elif duration_obj['type'] == 'instant':
            out = 'Instantaneous'
        elif duration_obj['type'] == 'permanent':
            out = 'Until '
            if 'dispel' in duration_obj['ends']:
                out += 'dispelled'
            if 'trigger' in duration_obj['ends']:
                out += 'or triggered'
        else:
            out = 'Special'
        return out

    def format_spell_components(components):
        out = ''
        if 'v' in components.keys():
            out += 'V, '
        elif 's' in components.keys():
            out += 'S, '
        elif 'm' in components.keys():
            if isinstance(components['m'], str):
                out += 'M ({0})'.format(components['m'])
            else:
                out += 'M ({0})'.format(components['m']['text'])

        if out[-2:] == ', ':
            out = out[:-2]
        return out

    def format_spell_range(range_obj):
        out = ''
        if range_obj['type'] == 'point':
            if range_obj['distance']['type'] in ['feet', 'miles']:
                out = '{0} {1}'.format(range_obj['distance']['amount'], range_obj['distance']['type'])
            else:
                out = range_obj['distance']['type'].capitalize()
        elif range_obj['type'] in ['radius', 'cone']:
            out = '{0} {1} radius'.format(range_obj['distance']['amount'], range_obj['distance']['type'])
        return out

    def format_spell_entries(entries):
        out = ''

        for entry in entries:
            if isinstance(entry, str):
                out += reformat_dice(entry) + '\n'
            else:
                out += entry['name'] + ' ' + format_spell_entries(entry.entries)
        return out

    embed = []
    name = spell['name']
    level = spell['level']
    school = format_spell_school(spell['school'])
    cast_time = '{0} {1}'.format(spell['time'][0]['number'],spell['time'][0]['unit'])
    is_ritual = 'meta' in spell and spell['meta']['ritual']
    duration = format_spell_duration(spell['duration'][0])

    rng = format_spell_range(spell['range'])
    components = format_spell_components(spell['components'])
    description = format_spell_entries(spell['entries'])
    ref = spell['source']
    desc = ""
    if level == '0':
        desc += school + " cantrip "
    else:
        desc += "level {0} {1}".format(level, school)

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

    if is_ritual:
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
    embed[len(embed) - 1].set_footer(text=footer)
    return embed


def format_monster(ctx, monster):
    name = monster['name']
    mytype = monster['type'] if isinstance(monster['type'], str) else monster['type']['type']
    caption = '*' + monster['size'] + ' ' + mytype + ', ALIGNMENT' + '*'
    ac = ''
    for ac_object in monster['ac']:
        if isinstance(ac_object, dict):
            ac += str(ac_object['ac']) + ' '
            if 'from' in ac_object:
                total_from = '('
                for f in ac_object['from']:
                    total_from += f + ','
                total_from = total_from[:-1]
                total_from += ')'
                ac += total_from + ', '
            elif 'cond' in ac_object:
                ac += ac_object['cond'] + ', '
        else:
            ac += str(ac_object) + ", "
        ac = ac[:-2]

    hp = str(monster['hp']['average']) + ' (' + monster['hp']['formula'] + ')'
    speed = ''
    for t, amt in monster['speed'].items():
        if t == 'walk':
            speed += str(amt) + ' ft., '
        else:
            speed += t + ' ' + str(amt) + ' ft., '

    speed = speed[:-2]

    stre = str(monster['str']) + ' (' + str(floor((monster['str'] - 10) / 2)) + ')'
    dex = str(monster['dex']) + ' (' + str(floor((monster['dex'] - 10) / 2)) + ')'
    con = str(monster['con']) + ' (' + str(floor((monster['con'] - 10) / 2)) + ')'
    int = str(monster['int']) + ' (' + str(floor((monster['int'] - 10) / 2)) + ')'
    wis = str(monster['wis']) + ' (' + str(floor((monster['wis'] - 10) / 2)) + ')'
    cha = str(monster['cha']) + ' (' + str(floor((monster['cha'] - 10) / 2)) + ')'

    source = monster['source'] + ' p. ' + str(monster['page'])
    snses = ''

    if 'senses' in monster:
        for c in monster['senses']:
            snses += c + ', '
    snses += 'passive Perception ' + str(monster['passive'])

    skills = ''
    if 'skill' in monster:
        for t, amt in monster['skill'].items():
            skills += t + ': ' + amt + ' ,'

        skills = skills[:-2]

    saves = ''
    if 'save' in monster:
        for t, amt in monster['save'].items():
            saves += t + ': ' + amt + ' ,'

        saves = saves[:-2]

    immune = ''

    if 'immune' in monster:
        for i in monster['immune']:
            if isinstance(i, str):
                immune += i + ', '
            else:
                immune += ', '.join(i['immune']) + ' ' + i['note']
        immune = immune[:-2]

    cndImmune = ''

    if 'conditionImmune' in monster:
        for i in monster['conditionImmune']:
            cndImmune += i + ', '
        cndImmune = cndImmune[:-2]

    vulnerable = ''
    if 'vulnerable' in monster:
        for i in monster['vulnerable']:
            if isinstance(i, str):
                vulnerable += i + ', '
            else:
                vulnerable += ', '.join(i['vulnerable']) + ' ' + i['note'] + '\n'
        vulnerable = vulnerable[:-2]

    lng = ''
    if 'languages' in monster:
        for l in monster['languages']:
            lng += l + ', '
        lng = lng[:-2]
    cr = monster['cr'] if isinstance(monster['cr'], str) else monster['cr']['cr']

    traits = ''

    if 'trait' in monster:
        for trait in monster['trait']:
            traits += '**' + trait['name'] + ':** '
            for e in trait['entries']:
                if isinstance(e, str):
                    traits += e
                else:
                    for inner in e['items']:
                        traits += '\n'
                        traits += '\u2022 **' + inner['name'] + ':** ' + inner['entry']
            traits += '\n'

    actions = ''

    if 'action' in monster:
        for action in monster['action']:
            actions += '**' + action['name'] + ':** '
            for e in action['entries']:
                if isinstance(e, str):
                    actions += e
                else:
                    # e is a dictionary, it has {style: dc, type: dc, items: [{name: string, entry: string, type: dc}]}
                    for inner in e['items']:
                        actions += '\n'
                        actions += '\u2022 **' + inner['name'] + ':** ' + inner['entry']
            actions += '\n\n'
    actions = reformat_dice(actions)
    reactions = ''

    if 'reaction' in monster:
        for r in monster['reaction']:
            reactions += '**' + r['name'] + ':** '
            for e in r['entries']:
                reactions += e
            reactions += '\n\n'
    reactions = reformat_dice(reactions)
    legendary = ''

    if 'legendary' in monster:
        for l in monster['legendary']:
            legendary += '**' + l['name'] + ':** '
            for e in l['entries']:
                legendary += e
            legendary += '\n\n'
    legendary = reformat_dice(legendary)

    return get_monster_embed(ctx, name, caption, ac, hp, speed, stre, dex, con, int, wis, cha, source, snses, skills
                             , saves, lng, immune, cndImmune, vulnerable, traits, actions, legendary, cr)


def get_monster_embed(ctx, name, caption, ac, hp, speed, stre, dex, con, inte, wis, cha, source, senses, skills, saves,
                      language, immunes, cndImmune, vulnerable, traits, actions, legendary, cr):
    color = random.randint(0, 0xffffff)
    firstE = discord.Embed()
    # create an embed that looks like Avrae's
    firstE.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    firstE.colour = color

    embeds = [firstE]

    embeds[-1].title = name

    description = caption + '\n' \
                  + '**AC:** ' + ac + '\n' \
                  + '**HP:** ' + hp +'\n' \
                  + '**Speed:** ' + speed + '\n' \
                  + '**STR:** ' + stre + ' **DEX:** ' + dex + ' **CON:** ' + con + '\n' \
                  + '**INT:** ' + inte + ' **WIS:** ' + wis + ' **CHA:** ' + cha + '\n' \
                  + ('**Skills:** ' + skills + '\n' if not skills == '' else '') \
                  + ('**Saves:** ' + saves + '\n' if not saves == '' else '') \
                  + ('**Immunities:** ' + immunes + '\n' if not immunes == '' else '') \
                  + ('**Condition Immunities:** ' + cndImmune + '\n' if not cndImmune == '' else '') \
                  + ('**Vulnerabilities:** ' + vulnerable + '\n' if not vulnerable == '' else '') \
                  + '**Senses:** ' + senses + '\n' \
                  + '**Languages:** ' + (language if not language == '' else '-') + '\n' \
                  + '**CR:** ' + cr

    embeds[-1].description = description

    def safe_append(title, desc):
        if len(desc) < 1024:
            embeds[-1].add_field(name=title, value=desc, inline=False)
        elif len(desc) < 2048:
            embeds.append(discord.Embed(colour=color, description=desc, title=title))
        else:
            embeds.append(discord.Embed(colour=color, title=title))
            trait_all = chunk_text(desc, max_chunk_size=2048)
            embeds[-1].description = trait_all[0]
            for t in trait_all[1:]:
                embeds.append(discord.Embed(colour=color, description=t))

    if not traits == '':
        safe_append('Traits', traits)
    if not actions == '':
        safe_append('Actions', actions)
    if not legendary == '':
        safe_append('Legendary Actions', legendary)

    embeds[-1].set_footer(text=source)
    return embeds


def chunk_text(text, max_chunk_size=1024, chunk_on=('\n\n', '\n', '. ', ' '), chunker_i=0):
    """
    Recursively chunks *text* into a list of str, with each element no longer than *max_chunk_size*.
    Prefers splitting on the elements of *chunk_on*, in order.
    """

    if len(text) <= max_chunk_size:  # the chunk is small enough
        return [text]
    if chunker_i >= len(chunk_on):  # we have no more preferred chunk_on characters
        # optimization: instead of merging a thousand characters, just use list slicing
        return [text[:max_chunk_size],
                *chunk_text(text[max_chunk_size:], max_chunk_size, chunk_on, chunker_i + 1)]

    # split on the current character
    chunks = []
    split_char = chunk_on[chunker_i]
    for chunk in text.split(split_char):
        chunk = f"{chunk}{split_char}"
        if len(chunk) > max_chunk_size:  # this chunk needs to be split more, recurse
            chunks.extend(chunk_text(chunk, max_chunk_size, chunk_on, chunker_i + 1))
        elif chunks and len(chunk) + len(chunks[-1]) <= max_chunk_size:  # this chunk can be merged
            chunks[-1] += chunk
        else:
            chunks.append(chunk)

    # remove extra split_char from last chunk
    chunks[-1] = chunks[-1][:-len(split_char)]
    return chunks
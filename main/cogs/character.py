from discord.ext import commands
from discord.commands import slash_command, Option
import main.character_manager as cm
import main.message_formatter as mf
from d20 import AdvType

SKILLS = [
    'acr',
    'ani',
    'arc',
    'ath',
    'dec',
    'his',
    'ins',
    'inti',
    'inv',
    'med',
    'nat',
    'perc',
    'perf',
    'pers',
    'rel',
    'sle',
    'ste',
    'sur'
]
MAIN_CHECKS = ['str', 'dex', 'con', 'int', 'wis', 'char']


class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def send_result(status, result, ctx):
        print(status)
        print(result)
        if status == cm.STATUS_OK:
            chat_result = ctx.author.mention + ":game_die: " + result
            await ctx.respond(chat_result)
        elif status == cm.STATUS_ERR:
            await ctx.respond('use `chimport` first!')
        elif status == cm.STATUS_INVALID_INPUT:
            await ctx.respond('Not a valid check!')

    @commands.command()
    async def chimport(self, ctx):
        if hasattr(ctx.message, 'attachments') and len(ctx.message.attachments) == 1:
            await ctx.send("Importing character. Please wait")
            xml_bytes = await ctx.message.attachments[0].read()
            data = cm.create_from_xml(xml_bytes)
            status = cm.import_from_object(data, ctx.author.id)
            if status == cm.STATUS_OK:
                _, char = cm.get_active_char(ctx.author.id)
                await ctx.send('Imported ' + char['name'])
            elif status == cm.STATUS_ERR:
                await ctx.send('There was an error while importing the character. Check logs!')
        else:
            await ctx.send('You need to upload your character file')

    @slash_command(guild_ids=[608192441333317683])
    async def chars(self, ctx):
        status, active_char = cm.get_active_char(ctx.author.id)
        if status == cm.STATUS_ERR:
            await ctx.respond("Could not retrieve your characters. Have you imported any yet?", ephemeral=True)
            return
        characters = cm.get_player_characters_list(ctx.author.id)
        msg_text = mf.format_characters(characters, ctx.author, active_char['_id'])
        await ctx.respond(msg_text, ephemeral=True)

    @slash_command(guild_ids=[608192441333317683])
    async def switch(self, ctx):
        characters = cm.get_player_characters_list(ctx.author.id)
        if len(characters) < 2:
            await ctx.respond("You have less than 2 imported characters. Use `/chars` to list your characters")
            return
        _, active_char = cm.get_active_char(ctx.author.id)
        char_names = [i['name'] for i in characters]

        async def on_reply(index, interaction):
            new_id = characters[index]['id']
            char = characters[index]
            success_msg = "I set your active character to: {0}".format(char['name'])
            if cm.switch_active_character(ctx.author.id, new_id):
                await interaction.response.edit_message(content=success_msg, view=None)

        await ctx.respond(content="Choose a new character from the dropdown below:",
                          view=mf.DropdownView(char_names, on_reply), ephemeral=True)

    @slash_command(guild_ids=[608192441333317683])
    async def del_char(self, ctx):
        characters = cm.get_player_characters_list(ctx.author.id)
        if len(characters) < 2:
            await ctx.respond("You have less than 2 imported characters. You cannot delete your last character!", ephemeral=True)
            return
        _, active_char = cm.get_active_char(ctx.author.id)
        inactive_chars = list(filter(lambda c: c['id'] != active_char['_id'], characters))
        char_names = [i['name'] for i in inactive_chars]

        async def on_reply(index, interaction):
            if index < len(inactive_chars):
                to_delete_id = inactive_chars[index]['id']
                char = characters[index]
                success_msg = "I deleted {0}".format(char['name'])
                if cm.delete_character(to_delete_id, ctx.author.id) > -99:
                    await interaction.response.edit_message(content=success_msg, view=None)
            else:
                await interaction.response.edit_message(content='Delete cancelled. Nothing was saved or deleted.', view=None)

        await ctx.respond(content="Choose a character to delete from below. *Note that this cannot be undone*",
                          view=mf.DropdownView(char_names, on_reply), ephemeral=True)

    @slash_command(guild_ids=[608192441333317683])
    async def check(self,
                    ctx,
                    attribute: Option(str, "Choose a check", choices=MAIN_CHECKS + SKILLS),
                    advantage: Option(str, "Advantage status", required=False, choices=["None", "Advantage", "Disadvantage"], default="None")):
        adv = AdvType.NONE

        if advantage == 'Advantage':
            adv = AdvType.ADV
        elif advantage == 'Disadvantage':
            adv = AdvType.DIS

        status, result = cm.roll_check(ctx.author.id, attribute, adv)
        await self.send_result(status, result, ctx)

    @slash_command(guild_ids=[608192441333317683])
    async def save(self, ctx,
                   attribute: Option(str, "Choose a save", choices=MAIN_CHECKS),
                   advantage: Option(str, "Advantage status", required=False, choices=["None", "Advantage", "Disadvantage"], default="None")):
        adv = AdvType.NONE

        if advantage == 'Advantage':
            adv = AdvType.ADV
        elif advantage == 'Disadvantage':
            adv = AdvType.DIS

        status, result = cm.roll_save(ctx.author.id, attribute, adv)
        await self.send_result(status, result, ctx)

    @slash_command(guild_ids=[608192441333317683])
    async def hp(self, ctx, modifier: Option(int, "HP Modifier", required=False, default=0)):
        status, cha = cm.get_active_char(ctx.author.id)
        if status == cm.STATUS_ERR:
            ctx.respond("Please import a character first. mK? thanks!")
        else:
            if modifier == 0 or modifier is None:
                await ctx.respond('{0}: {1}/{2}'.format(cha['name'], cha['HP'], cha['HPMax']))
            else:
                cm.update_character_hp(cha, modifier)

                if self.bot.cached_combat is None:
                    await ctx.respond('{0}: {1}/{2}'.format(cha['name'], cha['HP'], cha['HPMax']))
                else:
                    cbt = self.bot.cached_combat.get_combatant_from_name(cha['name'])
                    cbt.modify_health(modifier)
                    await ctx.respond(cbt.get_summary())
                    await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())


def setup(bot):
    bot.add_cog(Character(bot))
    print("Added Character Cog!")

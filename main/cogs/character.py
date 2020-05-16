from discord.ext import commands
import main.character_manager as cm
from d20 import AdvType


class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def send_result(status, result, ctx):
        print(status)
        print(result)
        if status == cm.STATUS_OK:
            chat_result = ctx.author.mention + ":game_die: " + result
            await ctx.send(chat_result)
        elif status == cm.STATUS_ERR:
            await ctx.send('use ?chimport first!')
        elif status == cm.STATUS_INVALID_INPUT:
            await ctx.send('Not a valid check!')

    @commands.command()
    async def chimport(self, ctx, arg):
        url = arg
        char_id = url.split("id=")[1]
        await ctx.send(
            "Importing character. Please wait ~~a while because miguel wants me to import from a pdf directly~~ :p")
        print("Importing from id: " + char_id)
        status = cm.import_from_drive_id(char_id, ctx.author.id)
        # cha = character.import_character_from_json((await message.attachments[0].read()).decode('utf-8'))
        # cha['_id'] = message.author.id
        # db.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
        if status == cm.STATUS_OK:
            _, char = cm.get_active_char(ctx.author.id)
            await ctx.send('Imported ' + char['PCName'])
        elif status == cm.STATUS_ERR_CHAR_EXISTS:
            await ctx.send(
                'A Character has already been imported from that url. If you need to update it, use `?chupdate` '
                'instead!')

    @commands.command(aliases=['ch'])
    async def check(self, ctx, *arg):
        adv = AdvType.NONE
        if len(arg) > 1:
            if 'adv' in arg[1].lower():
                adv = AdvType.ADV
            elif 'dis' in arg[1].lower():
                adv = AdvType.DIS

        status, result = cm.roll_check(ctx.author.id, arg[0], adv)
        await self.send_result(status, result, ctx)

    @commands.command(aliases=['s'])
    async def save(self, ctx, *args):
        adv = AdvType.NONE
        if len(args) > 1:
            if 'adv' in args[1].lower():
                adv = AdvType.ADV
            elif 'dis' in args[1].lower():
                adv = AdvType.DIS

        status, result = cm.roll_save(ctx.author.id, args[1], adv)
        await self.send_result(status, result, ctx)

    @commands.command()
    async def hp(self, ctx, *args):
        status, cha = cm.get_active_char(ctx.author.id)
        if status == cm.STATUS_ERR:
            ctx.send("3mol ma3roof import a character first thanks!")
        else:
            if len(args) == 0:
                await ctx.send('{0}: {1}/{2}'.format(cha['PCName'], cha['HP'], cha['HPMax']))
            else:
                mod = int(args[0])
                cha['HP'] += mod
                if cha['HP'] < 0:
                    cha['HP'] = 0
                if cha['HP'] > cha['HPMax']:
                    cha['HP'] = cha['HPMax']
                self.bot.database.chars.replace_one({'_id': cha['_id']}, cha, upsert=True)
                if self.bot.cached_combat is None:
                    await ctx.send('{0}: {1}/{2}'.format(cha['PCName'], cha['HP'], cha['HPMax']))
                else:
                    cbt = self.bot.cached_combat.get_combatant_from_name(cha['PCName'])
                    cbt.modify_health(mod)
                    await ctx.send(cbt.get_summary())
                    await self.bot.cached_combat.cached_summary.edit(content=self.bot.cached_combat.get_full_text())


def setup(bot):
    bot.add_cog(Character(bot))
    print("Added Character Cog!")

from discord.commands import application_command, SlashCommand
from main.data_manager import TEST_GUILD_ID


def my_slash_command(**kwargs):
    if TEST_GUILD_ID > 0:
        return application_command(cls=SlashCommand, guild_ids=[TEST_GUILD_ID], **kwargs)
    else:
        return application_command(cls=SlashCommand, **kwargs)
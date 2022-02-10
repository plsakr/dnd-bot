from discord.commands import application_command, SlashCommand
from main.data_manager import TEST_GUILD_ID


def my_slash_command(**kwargs):
    return application_command(cls=SlashCommand, **kwargs)

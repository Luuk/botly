import discord
from discord.ext import commands
from config import env


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_command_error(self, ctx, error):
        print(error)


bot = Bot()


@bot.event
async def on_ready():
    await bot.load_extension("commands.request_absence")
    await bot.load_extension("tasks")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!afwezig"))


bot.run(env.discord_bot_token)

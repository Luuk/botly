import discord
from discord.ext import commands
from config import env
import datetime

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_command_error(self, message, error):
        # Console error logging
        print(error)

        # Cooldown error message
        if isinstance(error, commands.CommandOnCooldown):
            await message.send(f"Je kunt dit pas over {error.retry_after:.0f} seconden weer doen.")


bot = Bot()


@bot.event
async def on_ready():
    await bot.load_extension("commands.request_absence")
    await bot.load_extension("tasks")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!afwezig"))


bot.run(env.discord_bot_token)

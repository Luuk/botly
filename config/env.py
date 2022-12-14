import discord
from dotenv import load_dotenv
import os

load_dotenv()

# Bot
discord_bot_token = str(os.getenv("DISCORD_BOT_TOKEN"))
absence_reminder_time = os.getenv("ABSENCE_REMINDER_TIME")

# Mongo Database
mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_url = os.getenv("MONGO_URL")

# Discord
private_review_channel_id = os.getenv("PRIVATE_REVIEW_CHANNEL_ID")
public_absence_channel_id = os.getenv("PUBLIC_ABSENCE_CHANNEL_ID")
botly_admin_role_id = os.getenv("BOTLY_ADMIN_ROLE_ID")
embed_color = discord.Color.from_str(os.getenv("EMBED_COLOR"))

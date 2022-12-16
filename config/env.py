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
mongo_database_name = os.getenv("MONGO_DATABASE_NAME")
mongo_absence_requests_collection_name = os.getenv("MONGO_ABSENCE_REQUESTS_COLLECTION_NAME")
mongo_users_collection_name = os.getenv("MONGO_USERS_COLLECTION_NAME")

# Discord
private_review_channel_id = os.getenv("PRIVATE_REVIEW_CHANNEL_ID")
public_absence_channel_id = os.getenv("PUBLIC_ABSENCE_CHANNEL_ID")
botly_admin_role_id = os.getenv("BOTLY_ADMIN_ROLE_ID")
embed_color = discord.Color.from_str(os.getenv("EMBED_COLOR"))

# Company
company_name = os.getenv("COMPANY_NAME")
company_domain = os.getenv("COMPANY_DOMAIN")

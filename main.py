import discord
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType
from dotenv import load_dotenv
import datetime
import os
import pymongo

# Dot ENV
load_dotenv()
reminder_time = os.getenv("REMINDER_TIME")

# Discord.Py config
private_review_channel = None
public_absence_channel = None
bot = commands.Bot(command_prefix="!", intents=discord.Intents().all())

# MongoDB config
mongo_client = pymongo.MongoClient(
    "mongodb+srv://Botly:S0tSHUc6jgdW6Iz7@cluster0.gdwtm0o.mongodb.net/?retryWrites=true&w=majority")
mongo_db = mongo_client["botly"]
mongo_col_absences = mongo_db['absences']


class DecisionView(discord.ui.View):
    def __init__(self, request_id, embed):
        self.request_id = request_id
        self.embed = embed
        super().__init__(timeout=None)

    @discord.ui.button(label="Goedkeuren", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.button):
        user_roles = interaction.user.roles
        has_permission = False

        # Check if user is permitted
        for role in user_roles:
            if int(role.id) == int(os.getenv("BOTLY_ADMIN_ROLE_ID")):
                has_permission = True

        if has_permission:
            # Update database request
            mongo_col_absences.update_one({'_id': self.request_id}, {
                "$set": {"accepted": True, "pending": False}})

            self.embed.title = "Afwezigheid"
            await public_absence_channel.send(embed=self.embed)

            self.embed.title = ":white_check_mark: Verzoek goedgekeurd"
            await interaction.user.send(embed=self.embed)

            button.disabled = True
            self.decline.disabled = True
            await interaction.response.edit_message(embed=self.embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Afwijzen", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.button):
        user_roles = interaction.user.roles
        has_permission = False

        # Check if user is permitted
        for role in user_roles:
            if int(role.id) == int(os.getenv("BOTLY_ADMIN_ROLE_ID")):
                has_permission = True

        if has_permission:
            # Update database request
            mongo_col_absences.update_one({'_id': self.request_id}, {
                "$set": {"pending": False}})

            self.embed.title = ":x: Verzoek afgewezen"
            await interaction.user.send(embed=self.embed)

            button.disabled = True
            self.accept.disabled = True
            await interaction.response.edit_message(embed=self.embed, view=self)
        else:
            await interaction.response.defer()


@bot.event
async def on_ready():
    # Global variables recommended refactor
    global private_review_channel
    private_review_channel = bot.get_channel(
        int(os.getenv("PRIVATE_REVIEW_CHANNEL_ID")))
    global public_absence_channel
    public_absence_channel = bot.get_channel(
        int(os.getenv("PUBLIC_ABSENCE_CHANNEL_ID")))
    reminder_loop.start()
    print(f'Logged in as {bot.user}')


# Check for absences and send reminder
@tasks.loop(seconds=10)
async def reminder_loop():
    if not datetime.datetime.now().time().strftime("%H:%M") == reminder_time:
        return

    current_date = datetime.datetime.now()

    pending_reminders = [
        {
            "$match": {
                "sent_reminder": False,
                "accepted": True,

                "start_datetime": {
                    "$gte": datetime.datetime(current_date.year, current_date.month, current_date.day, 0, 0),
                    "$lt": datetime.datetime(current_date.year, current_date.month, current_date.day, 23, 59)
                },

                "created_at": {
                    "$not": {
                        "$gte": datetime.datetime(current_date.year, current_date.month, current_date.day, 0, 0),
                        "$lt": datetime.datetime(current_date.year, current_date.month, current_date.day, 23, 59)
                    }
                }
            }
        }
    ]

    # Get today's absences that need to be reminded
    for absence in mongo_col_absences.aggregate(pending_reminders):
        embed = discord.Embed(
            title="Afwezigheid Reminder", color=0x9900ff)
        embed.add_field(
            name="Van", value="<@" + str(absence["user_id"]) + ">", inline=False)
        embed.add_field(name="Op", value="Vandaag", inline=True)
        embed.add_field(name="Van", value=absence["start_datetime"].strftime(
            "%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence["end_datetime"].strftime(
            "%H:%M uur"), inline=True)
        embed.add_field(name="Reden", value=str(
            absence["reason"]), inline=False)

        # Send reminder
        await public_absence_channel.send(embed=embed)

        # Update insert to sent_reminder = true
        mongo_col_absences.update_one({'_id': absence["_id"]}, {
            "$set": {"sent_reminder": True}})


# Request limit
@ bot.event
async def on_command_error(message, error):
    if isinstance(error, commands.CommandOnCooldown):
        await message.send(f"Je kunt dit pas over {round(error.retry_after / 60)} minuten opnieuw uitvoeren!")


@ bot.command()
@ commands.cooldown(1, 300, commands.BucketType.user)
async def afwezig(message):

    def check(m):
        return m.author.id == message.author.id

    if isinstance(message.channel, discord.channel.DMChannel):
        is_valid_start_date = False
        is_valid_full_day = False
        is_valid_start_time = False
        is_valid_end_time = False
        is_valid_reason = False

        # Get start date
        while not is_valid_start_date:
            await message.channel.send("Voer **datum** in (DD-MM-YYYY):")
            start_date = await bot.wait_for("message", check=check, timeout=60)
            start_date = convert_string_to_date(start_date.content)

            if not start_date or not is_valid_date(start_date):
                await message.channel.send("**Voer een geldige datum in!**")
            else:
                is_valid_start_date = True

        # Get full day
        while not is_valid_full_day:
            await message.channel.send("Hele dag? (Ja/Nee)")
            is_full_day = await bot.wait_for("message", check=check, timeout=60)
            is_full_day = is_full_day.content.lower()

            if is_full_day == "ja" or is_full_day == "nee":
                if is_full_day == "ja":
                    is_full_day = True
                    start_time = None
                    end_time = None
                else:
                    is_full_day = False

                is_valid_full_day = True
            else:
                await message.channel.send("**Voer een geldig antwoord in!**")

        # Get start time
        while not is_valid_start_time and not is_full_day:
            await message.channel.send("Voer **starttijd** in (HH:MM):")
            start_time = await bot.wait_for("message", check=check, timeout=60)
            start_time = convert_string_to_time(start_time.content)

            if start_time:
                is_valid_start_time = True
            else:
                await message.channel.send("**Voer een geldige starttijd in!**")

        # Get end time
        while not is_valid_end_time and not is_full_day:
            await message.channel.send("Voer **eindtijd** in (HH:MM):")
            end_time = await bot.wait_for("message", check=check, timeout=60)
            end_time = convert_string_to_time(end_time.content)

            if end_time:
                is_valid_end_time = True
            else:
                await message.channel.send("**Voer een geldige eindtijd in!**")

        # Get reason
        while not is_valid_reason:
            await message.channel.send("Voer **reden** in:")
            reason = await bot.wait_for("message", check=check, timeout=60)

            if len(reason.content.split()) < 200:
                is_valid_reason = True
            else:
                await message.channel.send("**Reden heeft een maximum van 200 woorden!**")

        # Convert to datetime
        if start_time == None and end_time == None:
            start_datetime = datetime.datetime.combine(
                start_date, datetime.time(9, 0))
            end_datetime = datetime.datetime.combine(
                start_date, datetime.time(17, 0))
        else:
            start_datetime = datetime.datetime.combine(start_date, start_time)
            end_datetime = datetime.datetime.combine(start_date, end_time)

        # Insert to database
        request_insert = mongo_col_absences.insert_one({"user_id": int(message.author.id), "created_at": datetime.datetime.now(), "start_datetime": start_datetime,
                                                       "end_datetime": end_datetime, "is_full_day": is_full_day, "reason": str(reason.content), "accepted": False, "pending": True, "sent_reminder": False})

        # Prepare absence request embed
        embed = discord.Embed(
            title="Afwezigheid aanvraag", color=0x9900ff)
        embed.add_field(
            name="Door", value="<@" + str(message.author.id) + ">", inline=False)
        embed.add_field(name="Op", value=start_datetime.strftime(
            "%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=start_datetime.strftime(
            "%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=end_datetime.strftime(
            "%H:%M uur"), inline=True)
        embed.add_field(name="Reden", value=str(reason.content), inline=False)

        await private_review_channel.send(embed=embed, view=DecisionView(request_id=request_insert.inserted_id, embed=embed))

        # Notify user
        await message.channel.send("Verzoek ingediend.")


def is_valid_date(date):
    # Check if date is not in the past
    if date < datetime.date.today():
        return False
    else:
        return True


def convert_string_to_date(date):
    try:
        date.split("-")[0]
        date.split("-")[1]
        date.split("-")[2]
    except IndexError:
        return False

    try:
        date = date.split("-")
        day = int(date[0])
        month = int(date[1])
        year = int(date[2])
        date = datetime.date(year, month, day)
    except ValueError:
        return False
    return date


def convert_string_to_time(time):
    try:
        time.split(":")[0]
        time.split(":")[1]
    except IndexError:
        return False

    try:
        hour = int(time.split(":")[0])
        minute = int(time.split(":")[1])
        time = datetime.time(hour, minute)
    except ValueError:
        return False
    return time


bot.run(os.getenv("DISCORD_BOT_TOKEN"))

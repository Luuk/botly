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
embed_color = discord.Color.from_str(os.getenv("EMBED_COLOR"))
bot = commands.Bot(command_prefix="!", intents=discord.Intents().all())

# MongoDB config
mongo_client = pymongo.MongoClient(
    "mongodb+srv://" + os.getenv("MONGO_USER") + ":" + os.getenv("MONGO_PASSWORD") + "@" + os.getenv("MONGO_URL"))
mongo_db = mongo_client["botly"]
mongo_col_absences = mongo_db['absences']


# Accept/Decline buttons
class DecisionView(discord.ui.View):
    def __init__(self, request_id, requester_user_id, embed):
        self.request_id = request_id
        self.requester_user_id = requester_user_id
        self.embed = embed
        super().__init__(timeout=None)

    @discord.ui.button(label="Goedkeuren", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        has_permission = False

        # Check if user is permitted
        for role in interaction.user.roles:
            if int(role.id) == int(os.getenv("BOTLY_ADMIN_ROLE_ID")):
                has_permission = True

        if has_permission:
            # Change embed in private channel
            button.disabled = True
            self.decline.disabled = True
            await interaction.message.edit(view=self)

            # Update database request
            mongo_col_absences.update_one({'_id': self.request_id}, {
                "$set": {"accepted": True, "pending": False}})

            # Change and send embed to requesting user
            self.embed.title = ":white_check_mark: Verzoek goedgekeurd"
            await interaction.message.edit(embed=self.embed)

            self.embed.remove_field(index=0)
            await bot.get_user(int(self.requester_user_id)).send(embed=self.embed)

            # Change and send embed in public channel
            self.embed.title = "Afwezigheid"
            self.embed.insert_field_at(index=0, name="Wie", value="<@" + str(self.requester_user_id) + ">",
                                       inline=False)
            self.embed.remove_field(index=4)
            # Needs to be done twice as the index changes
            self.embed.remove_field(index=4)
            await public_absence_channel.send(embed=self.embed)

    @discord.ui.button(label="Afwijzen", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        has_permission = False
        is_valid_decline_reason = False

        def user_check(m):
            return m.author.id == interaction.user.id

        # Check if user is permitted
        for role in interaction.user.roles:
            if int(role.id) == int(os.getenv("BOTLY_ADMIN_ROLE_ID")):
                has_permission = True

        if has_permission:
            # Change embed in private channel
            button.disabled = True
            self.accept.disabled = True
            await interaction.message.edit(view=self)

            # Get decline reason
            await interaction.channel.send("Voer **reden van afwijzing** in:")
            decline_reason = await bot.wait_for("message", check=user_check, timeout=200)

            # Update database request
            mongo_col_absences.update_one({'_id': self.request_id}, {
                "$set": {"pending": False, "decline_reason": str(decline_reason.content)}})

            # Change and send embed to requesting user
            self.embed.title = ":x: Verzoek afgewezen"
            self.embed.remove_field(index=0)
            self.embed.add_field(name="Waarom afgewezen", value=str(decline_reason.content), inline=False)
            await bot.get_user(int(self.requester_user_id)).send(embed=self.embed)
            await interaction.message.edit(embed=self.embed)


@bot.event
async def on_ready():
    # Global variables recommended refactor
    global private_review_channel
    private_review_channel = bot.get_channel(int(os.getenv("PRIVATE_REVIEW_CHANNEL_ID")))
    global public_absence_channel
    public_absence_channel = bot.get_channel(int(os.getenv("PUBLIC_ABSENCE_CHANNEL_ID")))

    reminder_loop.start()

    print(f'Logged in as {bot.user}')


# Check for absences and send reminder
@tasks.loop(seconds=10)
async def reminder_loop():
    # Check if current time is reminder time
    if not datetime.datetime.now().time().strftime("%H:%M") == reminder_time:
        return

    current_date = datetime.datetime.now()

    # MongoDB aggregation
    pending_reminders = [
        {
            "$match": {
                "sent_reminder": False,
                "accepted": True,
                # Get inserts where start_datetime is today
                "start_datetime": {
                    "$gte": datetime.datetime(current_date.year, current_date.month, current_date.day, 0, 0),
                    "$lt": datetime.datetime(current_date.year, current_date.month, current_date.day, 23, 59)
                },
                # Filter out inserts where created_at is today
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
        embed = discord.Embed(title="Afwezigheid Reminder", color=embed_color)
        embed.add_field(name="Wie", value="<@" + str(absence["user_id"]) + ">", inline=False)
        embed.add_field(name="Op", value="Vandaag", inline=True)
        embed.add_field(name="Van", value=absence["start_datetime"].strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence["end_datetime"].strftime("%H:%M uur"), inline=True)

        # Send reminder
        await public_absence_channel.send(embed=embed)

        # Update insert to sent_reminder = true
        mongo_col_absences.update_one({'_id': absence["_id"]}, {"$set": {"sent_reminder": True}})


# Request limit
@bot.event
async def on_command_error(message, error):
    if isinstance(error, commands.CommandOnCooldown):
        await message.send(f"Je kunt dit pas over {round(error.retry_after / 60)} minuten opnieuw uitvoeren!")


@bot.command()
@commands.cooldown(1, 100, commands.BucketType.user)
async def afwezig(message):
    def user_check(m):
        return m.author.id == message.author.id

    if isinstance(message.channel, discord.channel.DMChannel):
        is_valid_start_date = False
        is_valid_full_day = False
        is_valid_start_time = False
        is_valid_end_time = False
        is_valid_use_hours_choice = False
        is_valid_absence_reason = False

        # Get start date
        while not is_valid_start_date:
            await message.channel.send("Voer **datum** in (DD-MM-YYYY):")
            start_date = await bot.wait_for("message", check=user_check, timeout=60)
            start_date = convert_string_to_date(start_date.content)

            if not start_date or not is_valid_date(start_date):
                await message.channel.send("**Voer een geldige datum in!**")
            else:
                is_valid_start_date = True

        # Get full day
        while not is_valid_full_day:
            await message.channel.send("Hele dag? (Ja/Nee)")
            is_full_day = await bot.wait_for("message", check=user_check, timeout=60)
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
            await message.channel.send("Voer **starttijd** inclusief reistijd in (HH:MM):")
            start_time = await bot.wait_for("message", check=user_check, timeout=60)
            start_time = convert_string_to_time(start_time.content)

            if start_time:
                is_valid_start_time = True
            else:
                await message.channel.send("**Voer een geldige starttijd in!**")

        # Get end time
        while not is_valid_end_time and not is_full_day:
            await message.channel.send("Voer **eindtijd** inclusief reistijd in (HH:MM):")
            end_time = await bot.wait_for("message", check=user_check, timeout=60)
            end_time = convert_string_to_time(end_time.content)

            if end_time:
                is_valid_end_time = True
            else:
                await message.channel.send("**Voer een geldige eindtijd in!**")

        # Get user hours choice
        while not is_valid_use_hours_choice:
            await message.channel.send("Uren opnemen of later inhalen? (Opnemen/Inhalen):")
            use_hours_choice = await bot.wait_for("message", check=user_check, timeout=60)
            use_hours_choice = use_hours_choice.content.lower()

            if use_hours_choice == "opnemen" or use_hours_choice == "inhalen":
                if use_hours_choice == "opnemen":
                    use_hours_choice = "Ja"
                    use_hours_choice_boolean = True
                else:
                    use_hours_choice = "Nee"
                    use_hours_choice_boolean = False

                is_valid_use_hours_choice = True
            else:
                await message.channel.send("**Voer een geldig antwoord in!**")

        # Get absence reason
        while not is_valid_absence_reason:
            await message.channel.send("Voer **reden** in:")
            absence_reason = await bot.wait_for("message", check=user_check, timeout=60)

            if len(absence_reason.content.split()) < 200:
                is_valid_absence_reason = True
            else:
                await message.channel.send("**Reden heeft een maximum van 200 woorden!**")

        # Convert start & end dates to datetime format
        if start_time == None and end_time == None:
            start_datetime = datetime.datetime.combine(start_date, datetime.time(9, 0))
            end_datetime = datetime.datetime.combine(start_date, datetime.time(17, 0))
        else:
            start_datetime = datetime.datetime.combine(start_date, start_time)
            end_datetime = datetime.datetime.combine(start_date, end_time)

        # Insert to database
        request_insert = mongo_col_absences.insert_one(
            {
                "user_id": int(message.author.id),
                "created_at": datetime.datetime.now(),
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "is_full_day": is_full_day,
                "use_hours": use_hours_choice_boolean,
                "absence_reason": str(absence_reason.content),
                "accepted": False,
                "pending": True,
                "sent_reminder": False,
                "decline_reason": None
            }
        )

        # Prepare absence request embed
        embed = discord.Embed(title="Afwezigheid aanvraag", color=embed_color)
        embed.add_field(name="Door", value="<@" + str(message.author.id) + ">", inline=False)
        embed.add_field(name="Op", value=start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=use_hours_choice, inline=False)
        embed.add_field(name="Reden", value=str(absence_reason.content), inline=False)

        await private_review_channel.send(embed=embed, view=DecisionView(request_id=request_insert.inserted_id,
                                                                         requester_user_id=message.author.id,
                                                                         embed=embed))

        # Notify user
        await message.channel.send(embed=embed)


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

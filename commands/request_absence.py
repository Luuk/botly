import discord
from discord.ext import commands
import datetime
import utilities
from config import env
from config import database
from config.classes.absence_request_class import AbsenceRequest
from views.absence_request_view import AbsenceRequestView
from embeds.absence_request_embed import PrivateChannel, DirectMessage


class RequestAbsence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def afwezig(self, message):
        def user_check(m):
            return m.author.id == message.author.id

        if isinstance(message.channel, discord.channel.DMChannel):
            is_valid_start_date = False
            is_valid_full_day = False
            is_valid_start_time = False
            is_valid_end_time = False
            is_valid_use_hours = False
            is_valid_absence_reason = False

            # Get start date
            while not is_valid_start_date:
                await message.channel.send("Voer **datum** in (DD-MM-YYYY):")
                start_date = await self.bot.wait_for("message", check=user_check, timeout=60)
                start_date = utilities.convert_string_to_date(start_date.content)

                if not start_date or not utilities.is_valid_date(start_date):
                    await message.channel.send("**Voer een geldige datum in!**")
                else:
                    is_valid_start_date = True

            # Get full day
            while not is_valid_full_day:
                await message.channel.send("Hele dag? (Ja/Nee)")
                is_full_day = await self.bot.wait_for("message", check=user_check, timeout=60)
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
                start_time = await self.bot.wait_for("message", check=user_check, timeout=60)
                start_time = utilities.convert_string_to_time(start_time.content)

                if start_time:
                    is_valid_start_time = True
                else:
                    await message.channel.send("**Voer een geldige starttijd in!**")

            # Get end time
            while not is_valid_end_time and not is_full_day:
                await message.channel.send("Voer **eindtijd** inclusief reistijd in (HH:MM):")
                end_time = await self.bot.wait_for("message", check=user_check, timeout=60)
                end_time = utilities.convert_string_to_time(end_time.content)

                if end_time:
                    is_valid_end_time = True
                else:
                    await message.channel.send("**Voer een geldige eindtijd in!**")

            # Get use hours
            while not is_valid_use_hours:
                await message.channel.send("Uren opnemen of later inhalen? (Opnemen/Inhalen):")
                use_hours = await self.bot.wait_for("message", check=user_check, timeout=60)
                use_hours = use_hours.content.lower()

                if use_hours == "opnemen" or use_hours == "inhalen":
                    if use_hours == "opnemen":
                        use_hours = True
                    else:
                        use_hours = False

                    is_valid_use_hours = True
                else:
                    await message.channel.send("**Voer een geldig antwoord in!**")

            # Get absence reason
            while not is_valid_absence_reason:
                await message.channel.send("Voer **reden** in:")
                absence_reason = await self.bot.wait_for("message", check=user_check, timeout=60)

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

            # Create absence request object
            absence_request = AbsenceRequest(
                user_id=int(message.author.id),
                created_at=datetime.datetime.now(),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                is_full_day=is_full_day,
                use_hours=use_hours,
                absence_reason=str(absence_reason.content),
                is_accepted=False,
                is_pending=True,
                sent_reminder=False,
                request_decline_reason=None
            )

            # Insert object into database
            absence_request_insert = database.absences.insert_one(absence_request.__dict__)

            # Send embed with view
            await self.bot.get_channel(int(env.private_review_channel_id)).send(
                embed=PrivateChannel.pending(absence_request),
                view=AbsenceRequestView(absence_request, absence_request_insert.inserted_id))

            # Notify user
            await self.bot.get_user(int(absence_request.user_id)).send(embed=DirectMessage.pending(absence_request))


async def setup(bot):
    await bot.add_cog(RequestAbsence(bot))

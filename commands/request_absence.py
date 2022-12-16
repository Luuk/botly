import discord
from discord.ext import commands
import datetime
import re
from functions import utilities
from config import env
from config import database
from config.classes.absence_request_class import AbsenceRequest
from views.absence_request_view import AbsenceRequestView
from embeds.absence_request_embed import PrivateChannel, DirectMessage


class AbortWait(Exception):
    pass


class RequestAbsence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def afwezig(self, message):
        def user_check(m):
            if m.content == '!cancel':
                raise AbortWait()
            return m.author.id == message.author.id

        if isinstance(message.channel, discord.channel.DMChannel):
            user_email = await self.get_user_email(message, user_check)
            start_date = await self.get_start_date(message, user_check)
            end_time, is_full_day, start_time = await self.get_full_day_choice(message, user_check)
            start_time = await self.get_start_time(is_full_day, message, user_check)
            end_time = await self.get_end_time(is_full_day, message, user_check)
            use_hours = await self.get_use_hours(message, user_check)
            absence_reason = await self.get_absence_reason(message, user_check)
            end_datetime, start_datetime = await self.convert_to_datetime(end_time, start_date, start_time)
            absence_request = await self.create_absence_request_object(user_email, absence_reason, end_datetime,
                                                                       is_full_day,
                                                                       message, start_datetime, use_hours)
            absence_request_insert = database.absences.insert_one(absence_request.__dict__)
            await self.send_embed_to_private_channel(absence_request, absence_request_insert)
            await self.send_embed_to_user(absence_request)

    async def send_embed_to_user(self, absence_request):
        await self.bot.get_user(int(absence_request.discord_user_id)).send(embed=DirectMessage.pending(absence_request))

    async def send_embed_to_private_channel(self, absence_request, absence_request_insert):
        await self.bot.get_channel(int(env.private_review_channel_id)).send(
            embed=PrivateChannel.pending(absence_request),
            view=AbsenceRequestView(absence_request, absence_request_insert.inserted_id))

    async def create_absence_request_object(self, user_email, absence_reason, end_datetime, is_full_day, message,
                                            start_datetime,
                                            use_hours):
        absence_request = AbsenceRequest(
            discord_user_id=int(message.author.id),
            user_email=user_email,
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
        return absence_request

    async def get_user_email(self, message, user_check):
        user = database.users.find_one({"discord_user_id": int(message.author.id)})
        is_valid = False
        if not user:
            while not is_valid:
                await message.channel.send(f"Voer je **{env.company_name} email** in (eenmalig):")
                email = await self.bot.wait_for("message", check=user_check, timeout=60)

                if re.match(r"[^@]+@" + env.company_domain + "+", email.content):
                    database.users.insert_one({"discord_user_id": message.author.id, "email": email.content})
                    is_valid = True
                else:
                    await message.channel.send(f"**Voer een geldig {env.company_name} email in!**")
        else:
            email = user['email']
        return email

    async def convert_to_datetime(self, end_time, start_date, start_time):
        if start_time == None and end_time == None:
            start_datetime = datetime.datetime.combine(start_date, datetime.time(9, 0))
            end_datetime = datetime.datetime.combine(start_date, datetime.time(17, 0))
        else:
            start_datetime = datetime.datetime.combine(start_date, start_time)
            end_datetime = datetime.datetime.combine(start_date, end_time)
        return end_datetime, start_datetime

    async def get_absence_reason(self, message, user_check):
        is_valid = False
        while not is_valid:
            await message.channel.send("Voer **reden** in:")
            absence_reason = await self.bot.wait_for("message", check=user_check, timeout=60)

            if len(absence_reason.content.split()) < 200:
                is_valid = True
            else:
                await message.channel.send("**Reden heeft een maximum van 200 woorden!**")
        return absence_reason

    async def get_use_hours(self, message, user_check):
        is_valid = False
        while not is_valid:
            await message.channel.send("Uren opnemen of later inhalen? (Opnemen/Inhalen):")
            use_hours = await self.bot.wait_for("message", check=user_check, timeout=60)
            use_hours = use_hours.content.lower()

            if use_hours == "opnemen" or use_hours == "inhalen":
                if use_hours == "opnemen":
                    use_hours = True
                else:
                    use_hours = False

                is_valid = True
            else:
                await message.channel.send("**Voer een geldig antwoord in!**")
        return use_hours

    async def get_end_time(self, is_full_day, message, user_check):
        is_valid = False
        end_time = None
        while not is_valid and not is_full_day:
            await message.channel.send("Voer **eindtijd** inclusief reistijd in (HH:MM):")
            end_time = await self.bot.wait_for("message", check=user_check, timeout=60)
            end_time = utilities.convert_string_to_time(end_time.content)

            if end_time:
                is_valid = True
            else:
                await message.channel.send("**Voer een geldige eindtijd in!**")
        return end_time

    async def get_start_time(self, is_full_day, message, user_check):
        is_valid = False
        start_time = None
        while not is_valid and not is_full_day:
            await message.channel.send("Voer **starttijd** inclusief reistijd in (HH:MM):")
            start_time = await self.bot.wait_for("message", check=user_check, timeout=60)
            start_time = utilities.convert_string_to_time(start_time.content)

            if start_time:
                is_valid = True
            else:
                await message.channel.send("**Voer een geldige starttijd in!**")
        return start_time

    async def get_full_day_choice(self, message, user_check):
        is_valid = False
        while not is_valid:
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

                is_valid = True
            else:
                await message.channel.send("**Voer een geldig antwoord in!**")
        return end_time, is_full_day, start_time

    async def get_start_date(self, message, user_check):
        is_valid = False
        while not is_valid:
            await message.channel.send("Voer **datum** in (DD-MM-YYYY):")
            start_date = await self.bot.wait_for("message", check=user_check, timeout=60)
            start_date = utilities.convert_string_to_date(start_date.content)

            if not start_date or not utilities.is_valid_date(start_date):
                await message.channel.send("**Voer een geldige datum in!**")
            else:
                is_valid = True
        return start_date


async def setup(bot):
    await bot.add_cog(RequestAbsence(bot))

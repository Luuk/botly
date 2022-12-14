from discord.ext import commands, tasks
from config import env
from config import database
from config.classes.absence_request_class import AbsenceRequest
from embeds.absence_request_embed import PublicChannel
import datetime


utc = datetime.timezone.utc
time = datetime.time(
    hour=int(env.absence_reminder_time.split(":")[0]) - 1,
    minute=int(env.absence_reminder_time.split(":")[1]),
    tzinfo=utc
)


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.absence_reminder.start()

    def cog_unload(self):
        self.absence_reminder.cancel()

    @tasks.loop(time=time)
    async def absence_reminder(self):
        current_date = datetime.datetime.now()

        # MongoDB aggregation
        pending_reminders = [
            {
                "$match": {
                    "sent_reminder": False,
                    "is_accepted": True,
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
        for absence in database.absences.aggregate(pending_reminders):

            # Create absence request object
            absence_request = AbsenceRequest(
                user_id=int(absence['user_id']),
                created_at=absence['created_at'],
                start_datetime=absence['start_datetime'],
                end_datetime=absence['end_datetime'],
                is_full_day=absence['is_full_day'],
                use_hours=absence['use_hours'],
                absence_reason=str(absence['absence_reason']),
                is_accepted=absence['is_accepted'],
                is_pending=absence['is_pending'],
                sent_reminder=absence['sent_reminder'],
                request_decline_reason=absence['request_decline_reason']
            )

            # Send reminder
            await self.bot.get_channel(int(env.public_absence_channel_id)).send(embed=PublicChannel.reminder(absence_request))

            # Update insert to sent_reminder = true
            database.absences.update_one({'_id': absence["_id"]}, {"$set": {"sent_reminder": True}})


async def setup(bot):
    await bot.add_cog(Task(bot))

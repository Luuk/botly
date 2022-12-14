import discord
from config import env


class PrivateChannel:
    def pending(absence_request):

        # Change boolean to text
        if absence_request.use_hours:
            absence_request.use_hours = "Ja"
        else:
            absence_request.use_hours = "Nee"

        embed = discord.Embed(title=":alarm_clock: Afwezigheid aanvraag", color=env.embed_color)
        embed.add_field(name="Door", value=f"<@{str(absence_request.user_id)}>", inline=False)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=absence_request.use_hours, inline=False)
        embed.add_field(name="Reden", value=str(absence_request.absence_reason), inline=False)

        return embed

    def accepted(absence_request):

        # Change boolean to text
        if absence_request.use_hours:
            absence_request.use_hours = "Ja"
        else:
            absence_request.use_hours = "Nee"

        embed = discord.Embed(title=":white_check_mark: Verzoek goedgekeurd", color=env.embed_color)
        embed.add_field(name="Wie", value=f"<@{str(absence_request.user_id)}>", inline=False)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=absence_request.use_hours, inline=False)
        embed.add_field(name="Reden", value=str(absence_request.absence_reason), inline=False)

        return embed

    def declined(absence_request, request_decline_reason):

        # Change boolean to text
        if absence_request.use_hours:
            absence_request.use_hours = "Ja"
        else:
            absence_request.use_hours = "Nee"

        embed = discord.Embed(title=":x: Verzoek afgewezen", color=env.embed_color)
        embed.add_field(name="Wie", value=f"<@{str(absence_request.user_id)}>", inline=False)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=absence_request.use_hours, inline=False)
        embed.add_field(name="Reden", value=str(absence_request.absence_reason), inline=False)
        embed.add_field(name="Waarom afgewezen", value=str(request_decline_reason), inline=False)

        return embed


class PublicChannel:
    def accepted(absence_request):
        embed = discord.Embed(title=":alarm_clock: Afwezigheid", color=env.embed_color)
        embed.add_field(name="Wie", value=f"<@{str(absence_request.user_id)}>", inline=False)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)

        return embed

    def reminder(absence_request):
        embed = discord.Embed(title=":alarm_clock: Afwezigheid reminder", color=env.embed_color)
        embed.add_field(name="Wie", value=f"<@{str(absence_request.user_id)}>", inline=False)
        embed.add_field(name="Op", value="Vandaag", inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)

        return embed


class DirectMessage:
    def pending(absence_request):

        # Change boolean to text
        if absence_request.use_hours:
            absence_request.use_hours = "Ja"
        else:
            absence_request.use_hours = "Nee"

        embed = discord.Embed(title=":alarm_clock: Aanvraag ingediend", color=env.embed_color)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=absence_request.use_hours, inline=False)
        embed.add_field(name="Reden", value=str(absence_request.absence_reason), inline=False)

        return embed

    def accepted(absence_request):

        # Change boolean to text
        if absence_request.use_hours:
            absence_request.use_hours = "Ja"
        else:
            absence_request.use_hours = "Nee"

        embed = discord.Embed(title=":white_check_mark: Verzoek goedgekeurd", color=env.embed_color)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=absence_request.use_hours, inline=False)
        embed.add_field(name="Reden", value=str(absence_request.absence_reason), inline=False)

        return embed

    def declined(absence_request, request_decline_reason):

        # Change boolean to text
        if absence_request.use_hours:
            absence_request.use_hours = "Ja"
        else:
            absence_request.use_hours = "Nee"

        embed = discord.Embed(title=":x: Verzoek afgewezen", color=env.embed_color)
        embed.add_field(name="Op", value=absence_request.start_datetime.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Van", value=absence_request.start_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Tot", value=absence_request.end_datetime.strftime("%H:%M uur"), inline=True)
        embed.add_field(name="Uren opnemen", value=absence_request.use_hours, inline=False)
        embed.add_field(name="Reden", value=str(absence_request.absence_reason), inline=False)
        embed.add_field(name="Waarom afgewezen", value=str(request_decline_reason), inline=False)

        return embed

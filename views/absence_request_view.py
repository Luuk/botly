import discord
from config import env
from config import database
from embeds.absence_request_embed import PrivateChannel, PublicChannel, DirectMessage


class AbsenceRequestView(discord.ui.View):
    def __init__(self, absence_request, absence_request_insert_id):
        self.absence_request = absence_request
        self.absence_request_insert_id = absence_request_insert_id
        super().__init__(timeout=None)

    @discord.ui.button(label="Goedkeuren", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        has_permission = False

        # Check if user is permitted
        for role in interaction.user.roles:
            if int(role.id) == int(env.botly_admin_role_id):
                has_permission = True

        if has_permission:
            # Disable both buttons
            button.disabled = True
            self.decline.disabled = True

            # Update private channel embed
            await interaction.message.edit(view=self, embed=PrivateChannel.accepted(self.absence_request))

            # Update database insert
            database.absences.update_one({'_id': self.absence_request_insert_id}, {
                "$set": {"is_accepted": True, "is_pending": False}})

            # Send embed to user
            await interaction.client.get_user(int(self.absence_request.user_id)).send(
                embed=DirectMessage.accepted(self.absence_request))

            # Send embed to public absence channel
            await interaction.client.get_channel(int(env.public_absence_channel_id)).send(
                embed=PublicChannel.accepted(self.absence_request))

    @discord.ui.button(label="Afwijzen", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        has_permission = False

        def user_check(m):
            return m.author.id == interaction.user.id

        # Check if user is permitted
        for role in interaction.user.roles:
            if int(role.id) == int(env.botly_admin_role_id):
                has_permission = True

        if has_permission:
            # Disable both buttons
            button.disabled = True
            self.accept.disabled = True
            await interaction.message.edit(view=self)

            # Get request decline reason
            await interaction.channel.send("Voer **reden van afwijzing** in:")
            request_decline_reason = await interaction.client.wait_for("message", check=user_check, timeout=200)

            # Update private channel embed
            await interaction.message.edit(
                embed=PrivateChannel.declined(self.absence_request, str(request_decline_reason.content)))

            # Update database insert
            database.absences.update_one({'_id': self.absence_request_insert_id}, {
                "$set": {"is_pending": False, "request_decline_reason": str(request_decline_reason.content)}})

            # Send embed to user
            await interaction.client.get_user(int(self.absence_request.user_id)).send(
                embed=DirectMessage.declined(self.absence_request, str(request_decline_reason.content)))

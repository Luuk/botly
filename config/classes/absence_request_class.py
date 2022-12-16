class AbsenceRequest:
    def __init__(self, discord_user_id, user_email, created_at, start_datetime, end_datetime, is_full_day, use_hours, absence_reason,
                 is_accepted, is_pending, sent_reminder, request_decline_reason):
        self.discord_user_id = discord_user_id
        self.user_email = user_email
        self.created_at = created_at
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.is_full_day = is_full_day
        self.use_hours = use_hours
        self.absence_reason = absence_reason
        self.is_accepted = is_accepted
        self.is_pending = is_pending
        self.sent_reminder = sent_reminder
        self.request_decline_reason = request_decline_reason

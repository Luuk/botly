class AbsenceRequest:
    def __init__(self, user_id, created_at, start_datetime, end_datetime, is_full_day, use_hours, absence_reason,
                 is_accepted, is_pending, sent_reminder, request_decline_reason):
        self.user_id = user_id
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

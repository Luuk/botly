# Botly
Discord bot for Boldly-XR to handle absences.

## Prerequisites
### Software & services
- Python 3.11
- Pip 22.3.1
- MongoDB

### Packages
- discord.py 2.1.0
- python-dotenv 0.21.0
- pymongo 4.3.3

## Installation
1. Install required packages: `pip install -r requirements.txt`
2. Edit/configure `.env.example` and rename to `.env`
3. Follow header "Set up your environment" from [this guide](https://developers.google.com/calendar/api/quickstart/python), and place `credentials.json` in the `/config/google/` folder
3. Run `main.py`

NOTE: Running the bot for the first time will open an SSO to authenticate your Google Calendar.

## Usage
Users can start an absence request by DMing the bot `!afwezig`. This will trigger a function which starts asking the user the list of questions required for the request. Once this is complete, the request will be sent to the `PRIVATE_REVIEW_CHANNEL_ID` in which users with the `BOTLY_ADMIN_ROLE_ID` can accept or decline the request.

Accepted requests will be sent to the `PUBLIC_ABSENCE_CHANNEL_ID` so everyone can view it. Declined requests will not be shared publicly and only the user who created the request will be notified about the declinal.

Everyday, the bot checks which absences are that day, and will send a reminder for each of them at `ABSENCE_REMINDER_TIME` in the `PUBLIC_ABSENCE_CHANNEL_ID`.

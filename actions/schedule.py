import os
import yaml
import math
import nacl.secret

from typing import List
from dhooks import Webhook, Embed

from dateutil.parser import parse
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Imports to be removed(relying on setup()))
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import os.path

# NOTE: OPTIMISE AND REFACTOR CODE

# Load environment variables
load_dotenv()
TOKEN = os.environ['GCP_API_TOKEN']
RTOKEN = os.environ['GCP_REFRESH_TOKEN']
CLIENT_ID = os.environ['GCP_CLIENT_ID']
KEY = (int(os.environ['KEY'], 16)).to_bytes(32, 'big')
CLIENT_SECRET = os.environ['GCP_CLIENT_SECRET']

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def setup() -> None:
    """
    Initialisation Function
    The file token.json stores the user's access and refresh tokens, and is
    created automatically when the authorization flow completes for the first
    time.
    TODO - Remove function, and rely only on environment variables
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

def fetch_data_for(title: str) -> List[str]:
    for i in txt:
        if i.lower() in title:
            return txt[i]

def send_messages(info: List[str]) -> None:
    for i in info:
        data = fetch_data_for(i[26:].lower())
        if data:
            # Decrypt encrypted Webhook URL from yml file
            box = nacl.secret.SecretBox(KEY)
            url = box.decrypt(bytes(data[2], 'utf-8'), encoder=nacl.encoding.HexEncoder).decode('utf-8')
            hook = Webhook(url)
            embed = Embed(
                    title = f"**{i[26:]}**",
                    description=data[1],
                    color=0x0F2EEE)
            embed.add_field(name='\u200b', value=i[:25], inline=False)
            embed.set_thumbnail("https://images-ext-1.discordapp.net/external/9wjKKfnz90VR4MCxCu_KYVee6HDO8smJduqtL8dbNCs/%3Fsize%3D128/https/cdn.discordapp.com/icons/776352494992883722/0000b679a3e5f283653a38e138a43f9b.webp")
            embed.set_image(url=data[0])
            hook.send(embed=embed)
        # Cache data to file, to prevent multiple reminders
        write_to_file(info)

# TODO
def write_to_file(info: List[str]) -> None:
    """write what alerts have been made, to a file"""
    return

def main() -> None:
    """Initialise the calendar and sort data for upcoming events"""
    #setup()

    creds = Credentials(token=TOKEN, token_uri=TOKEN_URI,client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES, refresh_token=RTOKEN)
    service = build('calendar', 'v3', credentials=creds)
    results = service.calendarList().list().execute()
    # Fetch the TEC calendar
    cal_id = results['items'][0]['id']

    # Call the Calendar API
    now_ = datetime.utcnow().replace(tzinfo=timezone.utc)
    now = datetime.utcnow().isoformat() + 'Z'
    # Get the upcoming 5 events
    events_result = service.events().list(calendarId=cal_id, timeMin=now,
                                        maxResults=5, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    info = []

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = parse(event['start'].get('dateTime', event['start'].get('date')))

        # Filter out
        if math.floor(((start - now_).total_seconds()) // 3600) <= 1:
            info.append(f"{start} {event['summary']}")
        print(start, event['summary'])
    send_messages(info)

if __name__ == '__main__':
    with open("src/resources/templates.yml") as f:
        txt = yaml.safe_load(f)
    main()

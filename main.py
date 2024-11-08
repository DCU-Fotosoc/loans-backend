import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from config import Config

SERVICE_ACCOUNT_FILE = Config.GOOGLE_CALENDAR_CONFIG['SERVICE_ACCOUNT_FILE']
SCOPES = Config.GOOGLE_CALENDAR_CONFIG['SCOPES']
CALENDAR_ID = Config.GOOGLE_CALENDAR_CONFIG['CALENDAR_ID']
INVENTORY = Config.INVENTORY

SMTP_SERVER = Config.EMAIL_CONFIG['SMTP_SERVER']
SMTP_PORT = Config.EMAIL_CONFIG['SMTP_PORT']
EMAIL_ADDRESS = Config.EMAIL_CONFIG['EMAIL_ADDRESS']
EMAIL_PASSWORD = Config.EMAIL_CONFIG['EMAIL_PASSWORD']
REPLY_TO = Config.EMAIL_CONFIG['REPLY_TO']

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

def check_availability(item, quantity, start_time, end_time):
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    total_requested = 0

    for event in events:
        if event['summary'].startswith(item):
            event_quantity = int(event['summary'].split('- Qty: ')[1])
            total_requested += event_quantity

    available_quantity = INVENTORY.get(item, 0) - total_requested
    return available_quantity >= quantity, available_quantity

def send_email(to_email, subject, body):
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Reply-To'] = REPLY_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server.send_message(msg)
    server.quit()

def request_item(item, quantity, start_time, end_time, requester_email):
    try:
        is_available, available_quantity = check_availability(item, quantity, start_time, end_time)
        
        if not is_available:
            print(f"Requested quantity ({quantity}) for {item} not available. Only {available_quantity} available.")
            return

        event = {
            'summary': f'{item} - Qty: {quantity}',
            'description': f'{item} loan request by {requester_email}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }

        service = get_calendar_service()
        event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_link = event_result['htmlLink']

        print("Loan request approved and event created successfully!")
        print("Event ID:", event_result['id'])
        print("Event Link:", event_link)

        subject = f"Loan Request Approved: {item} - Qty: {quantity}"
        body = f"""Hello,

Your loan request for the following item has been approved:

Item: {item}
Quantity: {quantity}
Start: {start_time.isoformat()}
End: {end_time.isoformat()}
Link to the event: {event_link}

Thank you,
Photography Society
"""

        send_email(requester_email, subject, body)
        print(f"Confirmation email sent to {requester_email}")

    except Exception as e:
        print("Error:", str(e))

if __name__ == '__main__':
    item = 'Camera'
    quantity = 2
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=1, hours=2)
    requester_email = 'webmaster@dcufotosoc.ie'
    
    request_item(item, quantity, start_time, end_time, requester_email)

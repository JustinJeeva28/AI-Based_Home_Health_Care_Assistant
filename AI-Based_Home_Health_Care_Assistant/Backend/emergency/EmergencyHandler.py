from twilio.rest import Client
from config.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, USER_PHONE_NUMBER

def make_emergency_call(message):
    """Trigger an emergency call using Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=USER_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        twiml=f"<Response><Say>Emergency alert. {message}.</Say></Response>"
    )
    print(f'Call SID: {call.sid}')

def send_message(report):
    """Send the generated report as a message."""
    print(f"Sending the following report via message: {report}")
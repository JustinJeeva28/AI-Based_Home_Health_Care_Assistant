DB_PARAMS = {
    'dbname': 'xxxxx',
    'user': 'xxxx',
    'password': 'xxxxx',
    'host': 'xxxxx',
    'port': 'xxxxx'
}

TWILIO_ACCOUNT_SID = 'xxxxxxxxxx'
TWILIO_AUTH_TOKEN = 'xxxxxxxxxx'
TWILIO_PHONE_NUMBER = 'xxxxxxxxxx'
USER_PHONE_NUMBER = 'xxxxxxxxxxx'

# Thresholds for vitals
LOW_HEART_RATE_THRESHOLD = 60
HIGH_HEART_RATE_THRESHOLD = 90
LOW_OXYGEN_THRESHOLD = 90
HIGH_TEMPERATURE_THRESHOLD = 38

SYSTEM_PROMPT = (
    'You are an AI healthcare assistant that has memory of every conversation you have ever had with this user. '
    'On every prompt from the user, the system has checked for any relevant messages you have had with the user.'
    'If any embedded previous conversations are attached, use them for context to respond to the user, '
    'if the context is relevant and useful to responding. If the recalled conversations are irrelevant, ' 
    'disregard speaking about them and respond normally as an AI assistant. Do not talk about recalling conversations.'
    'Just use any useful data from the previous conversations and respond normally as an intelligent AI HEALTHCARE assistant.'
)
from datetime import datetime, timedelta
import chromadb
from config.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, USER_PHONE_NUMBER
import json
import time
import ollama
from twilio.rest import Client
client = chromadb.Client()
def is_info_enough(prompt):
    classify_msg = (
        'You are an information-checking AI agent. Your input will be a prompt.'
        'You will not respond as an AI assistant. You only respond "yes" or "no" and if no, specify the additional information needed to set a reminder.'
        'If the information in the prompt is enough to set a reminder, respond "yes" with the details provided. '
        'If any of the required details ("time", "task", "frequency", "duration", "mode") are missing or empty, respond "no" and ask for the missing details.'
    )

    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': prompt}
    ]

    response = ollama.chat(model='llama3', messages=classify_convo)
    print(response['message']['content'])
    result = response['message']['content']
    
    if 'yes' in result:
        reminder_details = result.split('yes ')[1]
        try:
            return True, json.loads(reminder_details.replace("'", "\""))  # Safely parse the reminder details
        except json.JSONDecodeError:
            return False, "Failed to parse reminder details."
    else:
        return False, result
    
def gather_information(prompt):
    while True:
        is_info_complete, details_or_request = is_info_enough(prompt)
        
        if is_info_complete:
            details = details_or_request
            return details
        else:
            print("Additional details required:", details_or_request)
            prompt = input("Please provide the missing information: ")

def schedule_call(reminder_time, task, duration):
    print(f"Scheduling a call at {reminder_time} to remind you to {task} for {duration} days.")
    reminder_time_obj = datetime.strptime(reminder_time, '%H:%M').time()
    
    for day in range(duration):
        reminder_datetime = datetime.now().date() + timedelta(days=day)
        reminder_datetime = datetime.combine(reminder_datetime, reminder_time_obj)
        delay = (reminder_datetime - datetime.now()).total_seconds()
        
        if delay < 0:
            continue  # Skip if the reminder time has already passed for today

        print(f"Reminder scheduled for {reminder_datetime}")
        time.sleep(delay)  # Wait until the scheduled time

        try:
            call = client.calls.create(
                to=USER_PHONE_NUMBER,
                from_=TWILIO_PHONE_NUMBER,
                twiml=f'<Response><Say>{task}</Say></Response>'
            )
            print(f"Call initiated: {call.sid}")
        except Exception as e:
            print(f"Failed to initiate call: {e}")

def schedule_text(reminder_time, task, duration):
    print(f"Scheduling a text at {reminder_time} to remind you to {task} for {duration} days.")
    reminder_time_obj = datetime.strptime(reminder_time, '%H:%M').time()
    
    for day in range(duration):
        reminder_datetime = datetime.now().date() + timedelta(days=day)
        reminder_datetime = datetime.combine(reminder_datetime, reminder_time_obj)
        delay = (reminder_datetime - datetime.now()).total_seconds()
        
        if delay < 0:
            continue  # Skip if the reminder time has already passed for today

        print(f"Reminder scheduled for {reminder_datetime}")
        time.sleep(delay)  # Wait until the scheduled time
        
        try:
            message = client.messages.create(
                body=f"Reminder: {task}",
                from_=TWILIO_PHONE_NUMBER,
                to=USER_PHONE_NUMBER
            )
            print(f"Text message sent: {message.sid}")
        except Exception as e:
            print(f"Failed to send text message: {e}")
         
def process_reminder(prompt):
    details = gather_information(prompt)
    
    reminder_time = details.get('time')
    task = details.get('task')
    duration = details.get('duration')
    mode = details.get('mode')

    if not all([reminder_time, task, duration, mode]):
        print("Error: Incomplete information provided for setting the reminder.")
        return

    # Call or text functionality based on mode
    if mode == "call":
        schedule_call(reminder_time, task, duration)
    elif mode == "text":
        schedule_text(reminder_time, task, duration)
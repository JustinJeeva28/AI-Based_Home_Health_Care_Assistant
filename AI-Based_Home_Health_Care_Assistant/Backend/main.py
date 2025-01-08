from health.vitals import check_vitals, vitals_check_loop
from health.HealthReport import report_generation , create_reports_table
from memory.ConversationMemory import  recall , fetch_conversations, create_vector_db,stream_response
from speech.SpeechProcessing import speech_to_text, text_to_speech
from reminder.reminder import process_reminder
from emergency.EmergencyHandler import make_emergency_call, send_message
from AI_Agents.Agents import classify_msg , health_history
from config.settings import SYSTEM_PROMPT
import threading
import time


def main_loop():
    """Main loop to handle user interaction and start the vitals check in parallel."""
    create_reports_table()  # Ensure the table exists
    # Start vitals check in a separate thread
    vitals_thread = threading.Thread(target=vitals_check_loop)
    report_thread = threading.Thread(target=report_generation)
    vitals_thread.daemon = True  # Ensure the thread exits when the main program does
    report_thread.daemon = True

    vitals_thread.start()
    report_thread.start()

    print("Starting main loop...")
    
    active = 0

    while True:
        user_input = speech_to_text()  # Replace with your actual speech-to-text function
        print(f'\nUSER: {user_input}\n')

        if active==0:
            if user_input != "Friday":
                text_to_speech("system activated")
                
            else:
                active = 1
        

        elif classify_msg(user_input) == 'emergency':  # Replace with your emergency classification function
            make_emergency_call(user_input)  # Replace with your emergency call function
            active = 0

        elif classify_msg(user_input) =='reminder query':
            # process_reminder(user_input)
            remainder_thread = threading.Thread(target=process_reminder(user_input))
            remainder_thread.daemon = True

            remainder_thread.start()
            active = 0
            
        else:
            health_history(user_input)
            conversations = fetch_conversations()  
            create_vector_db(conversations=conversations)  
            recall(prompt=user_input)  
            response = stream_response(prompt=user_input)  
            text_to_speech(response)  


if __name__ == "__main__":
    main_loop()
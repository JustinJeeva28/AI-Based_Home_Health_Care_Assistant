import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()

def text_to_speech(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def speech_to_text():
    """Convert speech to text."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, there was an issue with the request."
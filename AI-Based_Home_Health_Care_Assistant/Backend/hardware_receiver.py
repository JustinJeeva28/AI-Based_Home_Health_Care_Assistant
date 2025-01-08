import socket
import wave
import speech_recognition as sr

# Server configuration
server_ip = '0.0.0.0'  # Listen on all interfaces
server_port = 8888  # The port must match the one used in ESP32 code

def receive_audio():
    # Create and configure the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)
    
    print(f'Server listening on {server_ip}:{server_port}')
    
    conn, addr = server_socket.accept()
    print(f'Connected by {addr}')
    
    # Open file to save received audio
    with open('received_audio.raw', 'wb') as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    
    conn.close()
    server_socket.close()
    print('Audio received and saved to received_audio.raw')

def convert_to_wav(raw_audio_file, wav_audio_file):
    # Convert raw audio data to WAV format
    with open(raw_audio_file, 'rb') as rf:
        data = rf.read()
    
    with wave.open(wav_audio_file, 'wb') as wf:
        wf.setnchannels(1)  # Set the number of audio channels
        wf.setsampwidth(2)  # Set the sample width in bytes (16-bit audio)
        wf.setframerate(16000)  # Set the sample rate (must match ESP32)
        wf.writeframes(data)
    
    print(f'Audio converted to {wav_audio_file}')

def transcribe_audio(wav_audio_file):
    # Use SpeechRecognition to transcribe the WAV audio file
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(wav_audio_file) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f'Transcription: {text}')
    except sr.UnknownValueError:
        print('Google Speech Recognition could not understand audio')
    except sr.RequestError as e:
        print(f'Could not request results from Google Speech Recognition service; {e}')

if __name__ == '__main__':
    receive_audio()
    convert_to_wav('received_audio.raw', 'audio.wav')
    transcribe_audio('audio.wav')

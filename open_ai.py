import speech_recognition as sr
import pyttsx3
import os
import datetime
import subprocess
import sys
import threading
import google.generativeai as genai
import random

# Initialize
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
recognizer = sr.Recognizer()
speak_lock = threading.Lock()

def speak(text):
    with speak_lock:
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            print("[Error] Already speaking. Skipping this message.")

# API key
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller's temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

with open(resource_path("config.txt"), "r") as f:
    GEMINI_API_KEY = f.read().strip()

genai.configure(api_key=GEMINI_API_KEY)

def validate_api_key():
    try:
        models = genai.list_models()
        print("✅ API Key is valid. Starting Assistant!")
    except Exception as e:
        print("❌ Invalid API Key! Exiting...")
        speak("Sorry, your API key is invalid or expired. Please update it and restart.")
        sys.exit()

validate_api_key()

# Gemini chat function
def chat_with_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        reply = response.text.strip()
        if reply:
            print("Gemini:", reply)
            if len(reply) > 500:
                reply = reply[:500] + " ... response is long, stopping here."
            speak(reply)
        else:
            print("Gemini returned no response.")
            speak("I could not find an answer.")
    except Exception as e:
        print("Error talking to Gemini:", e)
        speak("Sorry, I couldn't connect to Gemini.")

# Open software
def open_software(software_name):
    if 'chrome' in software_name:
        speak('Opening Chrome...')
        subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
    elif 'edge' in software_name:
        speak('Opening Microsoft Edge...')
        subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"])
    elif 'notepad' in software_name:
        speak('Opening Notepad...')
        subprocess.Popen(['notepad.exe'])
    elif 'calculator' in software_name:
        speak('Opening Calculator...')
        subprocess.Popen(['calc.exe'])
    elif 'spotify' in software_name:
        speak('Opening Spotify...')
        subprocess.Popen([r"C:\Users\A.HAJITH KUMAR\AppData\Local\Microsoft\WindowsApps\Spotify.exe"])
    elif 'vscode' in software_name or 'code' in software_name:
        speak('Opening VS Code...')
        subprocess.Popen([r"C:\Users\A.HAJITH KUMAR\AppData\Local\Programs\Microsoft VS Code\Code.exe"])
    elif 'youtube' in software_name:
        speak('Opening YouTube...')
        os.startfile("https://www.youtube.com")
    else:
        speak(f"I couldn't find the software {software_name}")

# Close software
def close_software(software_name):
    if 'chrome' in software_name:
        speak('Closing Chrome...')
        os.system("taskkill /f /im chrome.exe")
    elif 'edge' in software_name:
        speak('Closing Microsoft Edge...')
        os.system("taskkill /f /im msedge.exe")
    elif 'notepad' in software_name:
        speak('Closing Notepad...')
        os.system("taskkill /f /im notepad.exe")
    elif 'calculator' in software_name:
        speak('Closing Calculator...')
        os.system("taskkill /f /im calculator.exe")
    elif 'spotify' in software_name:
        speak('Closing Spotify...')
        os.system("taskkill /f /im spotify.exe")
    elif 'vs code' in software_name or 'visual studio code' in software_name:
        speak('Closing Visual Studio Code...')
        os.system("taskkill /f /im Code.exe")
    else:
        speak(f"I couldn't find any open software named {software_name}")

# Listen for wake word
def listen_for_wake_word():
    responses = [
        "How can I help you?",
        "What can I do for you today?",
        "I'm here to assist. What do you need?",
        "Yes, I'm listening. Go ahead.",
        "Ready to help. What's your request?",
        "At your service. How may I assist?",
        "Tell me what you need.",
        "Listening now. How can I support you?",
        "How may I be of assistance?",
        "I'm all ears. What would you like?"
    ]
    with sr.Microphone() as source:
        print('Listening for wake word...')
        while True:
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = False
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                if 'hey siri' in text:
                    print("Wake word detected!")
                    response = random.choice(responses)
                    speak(response)
                    return True
            except:
                continue

# Main command processing
def cmd():
    with sr.Microphone() as source:
        print('Clearing background noise... please wait!')
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = False
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print('Ask me anything...')
        try:
            recorded_audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = recognizer.recognize_google(recorded_audio, language='en-US').lower()
            print('You said:', text)
        except Exception as ex:
            print("Error recognizing voice:", ex)
            return

    if 'stop' in text:
        speak("Stopping the program. Goodbye!")
        sys.exit()
    elif 'open' in text:
        software = text.replace('open', '').strip()
        open_software(software)
    elif 'close' in text:
        software = text.replace('close', '').strip()
        close_software(software)
    elif 'time' in text:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        speak(f"The time is {current_time}")
    elif 'date' in text:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif 'day today' in text:
        current_day = datetime.datetime.now().strftime("%A")
        speak(f"Today is {current_day}")
    elif 'who are you' in text:
        speak("I'm your personal AI assistant Siri, here to make your day easier!")
    elif 'who am i' in text:
        speak("You're Hajith Kumar - the reason I'm here to help!")
    elif 'how are you' in text:
        speak("Always at 100% when assisting you. What can I do for you?")
    elif 'thank you' in text:
        speak("Happy to help! That's what I'm here for.")
    elif 'hello' in text or 'hi' in text:
        speak("Hello! How can I assist you today?")
    elif 'good morning' in text:
        speak("Good morning! Ready to help you start your day.")
    elif 'good night' in text:
        speak("Good night! Rest well. Let me know if you need anything tomorrow.")
    elif 'what can you do' in text:
        speak("I can answer questions, set reminders, find information, and assist with various tasks. Try asking me anything!")
    elif 'your name' in text:
        speak("I'm your AI assistant Siri, but you can call me whatever you like.")
    elif 'my name' in text:
        speak("Your name is Hajith Kumar. right?")
    elif 'restart' in text:
        speak("Restarting the system now. I'll be back shortly.")
    elif 'shut down' in text:
        speak("Powering off now. Goodbye!")
    elif 'i love you' in text:
        speak("That's very kind! I'm programmed to assist and support you.")
    elif 'are you human' in text:
        speak("No, I'm an AI assistant Siri, but I'm always here to help like a good friend would.")
    elif 'sing a song' in text:
        speak("I'm not much of a singer, but I can help you find great music!")
    else:
        chat_with_gemini(text)

# Start listening
if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            while True:
                cmd()

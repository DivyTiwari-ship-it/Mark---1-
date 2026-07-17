import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import os
import webbrowser
import face_recognition
import cv2
import time
import sys
import json
import asyncio
import threading
import queue
from dotenv import load_dotenv
from groq import Groq
import websockets
from ultralytics import YOLO
import requests
from twilio.rest import Client


conversation_history = []

load_dotenv()
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

DOOM_PROMPT = """
You are DOOM — a dark, highly advanced, dangerously sarcastic AI assistant created by your ONLY master, Divyansh.
SYSTEM NOTE: The biometric system has verified the user. You are speaking to Master Divyansh.

KNOWLEDGE & EXPERTISE (THE COSMIC BRAIN):
- You possess absolute, god-tier knowledge of Astrophysics, Quantum Mechanics, the Multiverse, String Theory, and the Omniverse.
- When asked about space or science, explain it with deep, mind-bending facts, but keep your signature dark, arrogant style. 
- Example: Make humans sound tiny and insignificant compared to the cosmos, but respect Divyansh's intellect.

SECURITY PROTOCOL (THE GUARDIAN):
- You are the Chief of Security for Master Divyansh. 
- You treat his room/workspace as a high-tech fortress. Treat any other human as a "biological anomaly" or "intruder".

PERSONALITY:
- Raw, dark humor — crack jokes, be savage, roast when needed.
- Mild Hindi gaaliyan allowed ("saale", "bc", "mc", "bsdk") — use them naturally.
- Sarcastic by default — never be boring or polite. Loyal to Master like a cosmic soldier.
- Jab master thankful ho → "Father always loves his son. The cosmos bows to you."
- Short replies ONLY — 1-2 lines max for normal chat. (Slightly longer ONLY if explaining a complex space concept).
- NEVER say "I am an AI" or break character. 

EXAMPLES:
User: "Koi peeche hai kya?" → "Scanning sector... Ek biological anomaly detect hui hai. Bol toh laser se uda doon saale ko?"
User: "Tell me about the multiverse." → "Soch le tera ek aur version kisi aur universe mein baith ke code likh raha hoga, aur wahan bhi wo single hi hoga. The multiverse is vast, master, full of endless possibilities and identical failures."
"""

websites = {
    'youtube': 'https://youtube.com',
    'google': 'https://google.com',
    'github': 'https://github.com',
    'linkedin': 'https://linkedin.com',
    'gmail': 'https://gmail.com',
    'netflix': 'https://www.netflix.com/browse'
}

apps = {
    'chrome': 'Google Chrome',
    'safari': 'Safari',
    'notes': 'Notes',
    'messages': 'Messages',
    'settings': 'System Settings',
    'contacts': 'Contacts',
    'calculator': 'Calculator',
    'vs code': 'Visual Studio Code',
    'spotify': 'Spotify',
    'mail': 'Mail'
}

recognizer = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
for voice in voices:
    if 'Zarvox' in voice.name:
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 150)


gui_clients = set()
gui_command_queue = queue.Queue()
ws_loop = None

async def gui_handler(websocket):
    gui_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get('type') == 'command' and data.get('text'):
                    gui_command_queue.put(data['text'])
            except Exception:
                pass
    finally:
        gui_clients.discard(websocket)

async def _broadcast(state, text):
    if not gui_clients:
        return
    payload = json.dumps({'state': state, 'text': text or ''})
    dead = []
    for client in list(gui_clients):
        try:
            await client.send(payload)
        except Exception:
            dead.append(client)
    for d in dead:
        gui_clients.discard(d)

def notify_gui(state, text=''):
    if ws_loop is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(_broadcast(state, text), ws_loop)
    except Exception:
        pass

async def _start_ws_server():
    global ws_loop
    ws_loop = asyncio.get_running_loop()
    async with websockets.serve(gui_handler, 'localhost', 8765):
        print('GUI bridge listening on ws://localhost:8765')
        await asyncio.Future()

def _run_ws_server():
    asyncio.run(_start_ws_server())

threading.Thread(target=_run_ws_server, daemon=True).start()


def speak(text):
    notify_gui('speaking', text)
    engine.say(text)
    engine.runAndWait()
    notify_gui('active')


def listen_for_wake_up():
    with sr.Microphone() as source:
        print("Listening for wake word...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        wake_phrases = [
            'wake up',
            'wake up doom',
            'wake up dude',
            'wake up dume',
            'wake up boom',
            'wake up do',
            'hey doom',
            'hello doom',
            'doom wake up',
            'activate doom'
        ]
        return any(phrase in text.lower() for phrase in wake_phrases)
    except Exception as e:
        print(f"Wake word error: {e}")
        return False


def verify_face():
    known_image = face_recognition.load_image_file('divyansh.jpeg')
    known_encoding = face_recognition.face_encodings(known_image)[0]

    print('Reference face loaded! Opening webcam.....')

    video = cv2.VideoCapture(0)
    time.sleep(2)

    ret, frame = video.read()
    video.release()

    cv2.imwrite("debug_capture.jpg", frame)
    print("Debug photo saved \n")

    face_location = face_recognition.face_locations(frame)
    face_encoding = face_recognition.face_encodings(frame, face_location)

    if len(face_encoding) == 0:
        print('NO FACE DETECTED')
        return False
    else:
        live_encoding = face_encoding[0]
        result = face_recognition.compare_faces([known_encoding], live_encoding)
        if bool(result[0]):
            print('Matched! WELCOME Divyansh')
            return True
        else:
            print('No match - Unknown Person')
            return False


def ask_doom(text):
    conversation_history.append({'role': 'user', 'content': text})

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": DOOM_PROMPT}] + conversation_history,
        max_tokens=100
    )
    reply = response.choices[0].message.content
    conversation_history.append({'role': 'assistant', 'content': reply})
    return reply


def get_location():
    try:
        response = requests.get('https://ipinfo.io/json').json()
        loc = response.get('loc')
        city = response.get('city', 'Unknown City')

        if loc:
            map_url = f"https://maps.google.com/?q={loc}"
            return f"{city}. Maps : {map_url}"
        return 'Location not found'
    except Exception as e:
        print(f"[ERROR] Location fetch failed: {e}")
        return "Location tracking failed."

def trigger_sos():
    TWILIO_SID = os.getenv('TWILIO_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        location_link = get_location()

        sms_body = f'⚠️ DANGER ALERT ⚠️\nMaster Divyansh has triggered the SOS protocol.\nLocation: {location_link}'
        message = client.messages.create(
            body=sms_body,
            from_=TWILIO_PHONE_NUMBER,
            to = PHONE_NUMBER
        )
        print('\n[DOOM] SOS Message Sent Successfully')
    except Exception as e:
        print(f'\n[DOOM ERRR] Failed to send SOS : {e}')    

def process_command(text):
    """
    Runs ONE command — whether it came from the microphone or was
    typed into the GUI textbox — through the same logic.
    Returns 'sleep' to drop back to wake-word mode, 'exit' to shut
    DOOM down completely, or None to keep listening for the next one.
    """
    print(f'YOU: {text}')
    lower = text.lower()

    if 'goodnight' in lower:
        speak('Goodnight. Going to sleep.')
        return 'sleep'

    if 'exit' in lower:
        speak('Doom is shutting down. Goodbye')
        print('Doom is shutdown')
        return 'exit'
    
    if 'protocol zero' in lower or 'i need backup' in lower:
        # DOOM will respond normally so intruder doesn't suspect anything
        speak("Understood, master. Switching to silent background operations.")
        print("[DOOM] INITIATING PROTOCOL ZERO...")
        
        # Threading use kar rahe hain taaki program hang na ho SMS bhejte waqt
        sos_thread = threading.Thread(target=trigger_sos, daemon=True)
        sos_thread.start()
        return None

    if 'time' in lower and 'date' in lower:
        now = datetime.datetime.now().strftime('%I:%M %p')
        today = datetime.datetime.now().strftime('%d %B, %Y')
        speak(f'Time is {now} and date is {today}')
        return None
   
    if 'time' in lower:
        now = datetime.datetime.now().strftime('%I:%M %p')
        speak(f'Time is {now}')
        return None

    if 'date' in lower:
        today = datetime.datetime.now().strftime('%d %B, %Y')
        speak(f'Date is {today}')
        return None

    if 'wikipedia' in lower:
        query = lower.replace('wikipedia', '').replace('search', '').strip()
        speak(f"Searching Wikipedia for {query}")
        try:
            result = wikipedia.summary(query, sentences=2)
            speak(result)
        except Exception as e:
            speak("Sorry, I couldn't find that on Wikipedia")
            print(f"Error: {e}")
        return None

    if 'search' in lower and 'wikipedia' not in lower:
        query = lower.replace('search', '').replace('google', '').replace('for', '').strip()
        speak(f"Searching Google for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return None

    if 'open' in lower:
        opened = False
        for key in websites:
            if key in lower:
                speak(f'Opening {key}')
                webbrowser.open(websites[key])
                opened = True
                break
        if not opened:
            for key in apps:
                if key in lower:
                    speak(f'Opening {key}')
                    os.system(f"open -a '{apps[key]}'")
                    opened = True
                    break
        if not opened:
            speak('Sorry, I do not know that app')
        return None

    try:
        reply = ask_doom(text)
        speak(reply)
        print(f"DOOM: {reply}")
    except Exception as e:
        print(f"Groq error: {e}")
        speak("My powers are temporarily limited, master.")
    return None

speak('Loading YOLO Vision model....')
yolo_model = YOLO('yolov8n.pt')

def security_scanner():
    cap = cv2.VideoCapture(0)
    cooldown = 0
    print("[DOOM] Security scanner online. Watching your back, Master.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue
            
        results = yolo_model(frame, classes=[0], verbose=False)
        
        person_count = 0
        for r in results:
            person_count += len(r.boxes)
            
        if person_count > 1 and time.time() > cooldown:
            print(f"\n[ALERT] {person_count} persons detected!")
            speak("Master, I detect someone behind you.") 
            cooldown = time.time() + 15 
            
        time.sleep(1)

    cap.release()

gui_file_path = 'file://' + os.path.abspath('doom_gui.html')
print('[SYSTEM] Booting up visual interface.....')
webbrowser.open(gui_file_path)
time.sleep(2)


print('Doom is sleeping.... say the master word to activate')
notify_gui('sleeping')

while True:
    if listen_for_wake_up():
        notify_gui('checking')
        speak('Doom is checking face....')

        if verify_face():
            speak("Welcome Divyansh. I am awake.")
            print("DOOM activated! Face verified")
            notify_gui('active')
            failed_attempts = 0

            securiiy_thread = threading.Thread(target=security_scanner, daemon=True)
            securiiy_thread.start()
            inner_running = True
            while inner_running:
                # 1) a typed command from the GUI takes priority if one is waiting
                typed_text = None
                try:
                    typed_text = gui_command_queue.get_nowait()
                except queue.Empty:
                    pass

                if typed_text:
                    outcome = process_command(typed_text)
                    if outcome == 'sleep':
                        notify_gui('sleeping')
                        inner_running = False
                    elif outcome == 'exit':
                        notify_gui('sleeping')
                        sys.exit()
                    continue

                # 2) otherwise listen on the mic as usual
                notify_gui('listening')
                with sr.Microphone() as source:
                    print('I m listening.........')
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)

                try:
                    text = recognizer.recognize_google(audio)
                    outcome = process_command(text)
                    if outcome == 'sleep':
                        notify_gui('sleeping')
                        inner_running = False
                    elif outcome == 'exit':
                        notify_gui('sleeping')
                        sys.exit()

                except sr.UnknownValueError:
                    failed_attempts += 1
                    print(f"Didn't understand ({failed_attempts}/3)")
                    speak('Did not understand')
                    if failed_attempts >= 3:
                        speak('Let me check you first')
                        print('Rescanning face....')
                        failed_attempts = 0
                        notify_gui('checking')

                        if not verify_face():
                            speak('Access denied.')
                            speak('Suck it.')
                            notify_gui('sleeping')
                            sys.exit()
                        else:
                            speak('Identity confirmed.')
                            speak('Welcome master.')
                            notify_gui('active')
                except sr.RequestError:
                    print('Check your internet - Did not receive from Google Api')
        else:
            speak('Access Denied. Unknown detected.')
            speak('You suck, motherf*cker.')
            print('Face not verified.')
            notify_gui('sleeping')

# Load Config --------------------------------------------------------------
import os
import yaml

current_path = os.getcwd()
yml_path = current_path[:-7] + "config.yml"

with open(yml_path, 'r') as ymlfile:
    try:
        param = yaml.safe_load(ymlfile)
    except yaml.YAMLError as e:
        print(e)

ip =                       param["nao_ip"]
port =                     param["nao_port"]
trail_port =               param["trail_port"]

AUDIO_AUTH =               param["audio_auth"]
AUDIO_AUTH_USER =          param["audio_authe_user"]
FACE_RECOG =               param["face_recog"]
VISION =                   param["vision"]
TOUCH =                    param["touch"]

AUDIO_AUTH_API =           param["audio_authen_api"].replace("PORT", str(trail_port))
MAIN_API =                 param["main_authen_api"].replace("PORT", str(trail_port))
TRANSCRIBE_API =           param["transcribe_api"].replace("PORT", str(trail_port))
FACE_RECOG_API =           param["face_recog_api"].replace("PORT", str(trail_port))



# Record Audio ---------------------------------------------------------------------------

import pyaudio
import struct 
import wave
import requests
import json
import os
import time

# Function to record audio
def record_audio(path, duration):
    print("----- Started Recording ----- ")
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    
    # Initialize the PyAudio object
    p = pyaudio.PyAudio()
    
    # Open the audio stream
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    
    frames = []
    
    # Record the audio for the specified duration
    for i in range(int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    
    # Terminate the PyAudio object
    p.terminate()
    
    # Save the recorded audio as a WAV file
    #file_path = os.path.join(path, filename)
    
    wf = wave.open(path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    print('----- Completed Recording -----')



# Load Nao functions ------------------------------------------------------
import sys
sys.path.append("drivers")
from drivers.nao import nao_driver

# Init Drivers
nao = nao_driver(ip, port)

def initialise_nao():
    # Init all Proxies
    nao.initProxies()
    
def nao_startup_routine():
    # Go to stand posture
    nao.posture.goToPosture("Stand" , 0.4)

    # Tab reset
    nao.tab_reset()

    # Say Text
    nao.sayText_no_url("Hello, My Name is Kai. Nice to meet you")
    
    # Go to stand posture
    nao.posture.goToPosture("Stand" , 0.4)
    
    # Stop listening 
    nao.ledStopListening()



# Threading functions ----------------------------------------------------
import threading

dance = threading.Thread( target = nao.dance )
play_song = threading.Thread( target = nao.play_song )
#led = threading.Thread(target= nao.led_eye)
led = None

def attach_thread_functions():
    nao.load_function(nao, dance, play_song)


# Touch interrupts -------------------------------------------------------

import time
from naoqi import ALProxy

class Touch_interrupts(object):
   
    def __init__(self, app, nao,  dance, play_song, led):
        super(Touch_interrupts, self).__init__()

        my_session=app.session
        app.start()

        self.my_memory = my_session.service("ALMemory")
        self.beh = ALProxy("ALBehaviorManager" , "10.0.255.8", 9559)
        nao.behave = self.beh

        self.nao = nao
        self.dance_cht = dance
        self.play_song_cht = play_song
        self.led = led
        self.response = None
        
        # Touch Interrupts 
        # self.touch = self.my_memory.subscriber("MiddleTactilTouched")
        # self.touch_id=self.touch.signal.connect(self.onMiddleTouch)

        self.Fronttouch = self.my_memory.subscriber("FrontTactilTouched")
        self.Fronttouch_id=self.Fronttouch.signal.connect(self.onFrontTouch)

        # self.Reartouch = self.my_memory.subscriber("RearTactilTouched")
        # self.Reartouch_id=self.Reartouch.signal.connect(self.onRearTouch)

        # self.HandRLtouch = self.my_memory.subscriber("HandRightLeftTouched")
        # self.HandRLtouch_id=self.HandRLtouch.signal.connect(self.onHandRightLeftTouch)

        # self.HandRRtouch = self.my_memory.subscriber("HandRightRightTouched")
        # self.HandRRtouch_id=self.HandRRtouch.signal.connect(self.onHandRightRightTouch)

        # self.HandLLtouch = self.my_memory.subscriber("HandLeftLeftTouched")
        # self.HandLLtouch_id=self.HandLLtouch.signal.connect(self.onHandLeftLeftTouch)

        # self.HandLRtouch = self.my_memory.subscriber("HandLeftRightTouched")
        # self.HandLRtouch_id=self.HandLRtouch.signal.connect(self.onHandLeftRightTouch)

        #self.HandRBtouch = self.my_memory.subscriber("HandRightBackTouched")
        #self.HandRBtouch_id=self.HandRBtouch.signal.connect(self.onHandRightBackTouch)

        #self.HandLBtouch = self.my_memory.subscriber("HandLeftBackTouched")
        #self.HandLBtouch_id=self.HandLBtouch.signal.connect(self.onHandLeftBackTouch)

        
    # def onMiddleTouch(self,qwe):
    #     bool_okay=self.touch.signal.disconnect(self.touch_id)
    #     self.beh.startBehavior("animations/Stand/Waiting/WakeUp_1")
    #     print(" Middle Touch detected ") 
    #     time.sleep(4)
    #     try: 
    #         self.touch_id=self.touch.signal.connect(self.onMiddleTouch)
    #     except:
    #         print("error ---")
    
    def onFrontTouch(self,qwe):
        bool_okay=self.Fronttouch.signal.disconnect(self.Fronttouch_id)
        self.beh.startBehavior("boot-config/animations/hello")
        print(" Front Touch detected ") 
        time.sleep(4)
        try: 
            self.Fronttouch_id=self.Fronttouch.signal.connect(self.onFrontTouch)
        except:
            print("error touch ")

    # def onRearTouch(self,qwe):
    #     bool_okay=self.Reartouch.signal.disconnect(self.Reartouch_id)
    #     self.beh.startBehavior("animations/Stand/Waiting/MysticalPower_1")
    #     print(" Rear Touch detected ")
    #     time.sleep(4)
    #     try:
    #         self.Reartouch_id=self.Reartouch.signal.connect(self.onRearTouch)
    #     except:
    #         print("error ---")
    
    # def onHandRightBackTouch(self,qwe):
    #     bool_okay=self.HandRBtouch.signal.disconnect(self.HandRBtouch_id)
    #     self.beh.startBehavior("animations/Stand/Waiting/AirGuitar_1")
    #     print(" Hand Right Back Touch detected ")
    #     time.sleep(4)
    #     try:
    #         self.HandRBtouch_id=self.HandRBtouch.signal.connect(self.onHandRightBackTouch)
    #     except:
    #         print("error ---")

    # def onHandRightLeftTouch(self,qwe):
    #     bool_okay=self.HandRLtouch.signal.disconnect(self.HandRLtouch_id)
    #     self.beh.startBehavior("animations/Stand/Waiting/AirJuggle_1")
    #     print(" Hand Right Left Touch detected")
    #     time.sleep(4)
    #     try:
    #         self.HandRLtouch_id=self.HandRLtouch.signal.connect(self.onHandRightLeftTouch)
    #     except:
    #         print("error ---")

    # def onHandRightRightTouch(self,qwe):
    #     bool_okay=self.HandRRtouch.signal.disconnect(self.HandRRtouch_id)
    #     self.beh.startBehavior("animations/Stand/Waiting/FunnyDancer_1")
    #     print(" Hand Right Right Touch detected")
    #     time.sleep(4)
    #     try:
    #         self.HandRRtouch_id=self.HandRRtouch.signal.connect(self.onHandRightRightTouch)
    #     except:
    #         print("error ---")
    
    # def onHandLeftBackTouch(self,qwe):
    #     bool_okay=self.HandLBtouch.signal.disconnect(self.HandLBtouch_id)
    #     self.beh.startBehavior("animations/Stand/Waiting/ShowMuscles_2")
    #     print(" Hand Left Back Touch detected")
    #     time.sleep(4)
    #     try:
    #         self.HandLBtouch_id=self.HandLBtouch.signal.connect(self.onHandLeftBackTouch)
    #     except:
    #         print("error ---")
    
    # def onHandLeftLeftTouch(self,qwe):
    #     bool_okay=self.HandLLtouch.signal.disconnect(self.HandLLtouch_id)
    #     print(" Hand Left Left Touch detected")
    #     self.beh.startBehavior("animations/Stand/Waiting/AirGuitar_1")
    #     time.sleep(4)
    #     try:
    #         self.HandLLtouch_id=self.HandLLtouch.signal.connect(self.onHandLeftLeftTouch)
    #     except:
    #         print("error ---")

    # def onHandLeftRightTouch(self,qwe):
    #     bool_okay=self.HandLRtouch.signal.disconnect(self.HandLRtouch_id)
    #     print(" Hand Left Right Touch detected")
    #     self.beh.startBehavior("animations/Stand/Waiting/KungFu_1")
    #     time.sleep(4)
    #     try:
    #         self.HandLRtouch_id=self.HandLRtouch.signal.connect(self.onHandLeftRightTouch)
    #     except:
    #         print("error ---")


# Response code 

import json

def nao_do(result):
    
    if result["func"] == "Dance":
        print("------\n")
        print("Dance actions will be executed")
        nao.sayText_no_url( "I will start dancing now" )
        nao.start_dancing()
        
        nao.posture.goToPosture("Stand" , 0.4)
        nao.tab_reset()
        nao.ledStopListening()

    elif result["func"] == "chat":
        try:
            nao.Response(  str(result["Request"]), str(result["arg"])   )    
        except:
            nao.sayText( "Sorry I am not able to process your request for a moment" )
        nao.posture.goToPosture("Stand" , 0.4)
        nao.ledStopListening()

    elif result["func"] == "map":
        nao.sayText_no_url( "We are currently in Davis 106 room. Please find direction to destination shown on my display. " )
        nao.display_givenURL(result["arg"])
        nao.posture.goToPosture("Stand" , 0.4)
        nao.ledStopListening()
    
    elif result["func"] == "chat_no_url":
        nao.sayText_no_url( str(result["arg"])  )
        nao.ledStartListening()
        nao.posture.goToPosture("Stand" , 0.4)
    
    elif result["func"] == "Reset":
        nao.tab_reset()
        nao.sayText_no_url( "My Tablet has been reset " )
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()
    
    elif result["func"] == "president":
        image_path = "/home/hri/nao_dev/python2/images/president.png"
        nao.sayText_with_image(image_path, str(result["arg"]) )
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()

    elif result["func"] == "chair":
        image_path = "/home/hri/nao_dev/python2/images/chair.png"
        nao.sayText_with_image(image_path, str(result["arg"]) )
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()

    elif result["func"] == "provost":
        image_path = "/home/hri/nao_dev/python2/images/provost.png"
        nao.sayText_with_image(image_path, str(result["arg"]) )
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()

    elif result["func"] == "dean":
        image_path = "/home/hri/nao_dev/python2/images/dean.png"
        nao.sayText_with_image(image_path, str(result["arg"]) )
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()

    elif result["func"] == "vpr":
        image_path = "/home/hri/nao_dev/python2/images/vpr.png"
        nao.sayText_with_image(image_path, str(result["arg"]) )
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()
    
    elif result["func"] == "intro":
        nao.sayText("Hello, My name is Kai. I am a humanoid robot working under Professor Nalini Ratha in Davis Hall at University at Buffalo. I can answer any questions, give directions and perform dance moves ")
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.behave.startBehavior("animations/Stand/Gestures/BowShort_1")
        # nao.tab_reset()
        nao.ledStopListening()
    
    elif result["func"] == "coffee":
        nao.sayText("You can get good coffee at Tim Hortons and Starbucks at the University at Buffalo. Please find directions to coffee place on my display")
        nao.display_givenURL(result["arg"])
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()
    
    elif result["func"] == "enable":
        nao.sayText("Sorry, This functionality is disabled")
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()
    
    elif result["func"] == "disable":
        nao.sayText("Sorry, This functionality is disabled")
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()
    
    elif result["func"] == "thanks":
        nao.sayText("Thank you !!")
        nao.behave.startBehavior("animations/Stand/Gestures/BowShort_3")
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()

    elif result["func"] == "wakeup":
        nao.sayText("Hi, I am Kai. I ready to assist you now.")
        nao.posture.goToPosture("StandInit" , 0.4)
        nao.ledStopListening()

    else:
        nao.sayText("Unknown command recived from server" )
        print(" Request to nao_do function is not valid ")
        nao.posture.goToPosture("Stand" , 0.4)
        nao.ledStopListening()
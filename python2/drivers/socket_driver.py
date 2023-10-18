import socket 
import pickle
import threading
import ast
import time
from naoqi import ALProxy

class chatGPT(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.gui_socket = None

        self.dance_sckt = None
        self.play_song_sckt = None
        self.nao = None

    def load_function(self, nao, dance, play_song):
        self.nao = nao
    
    def start_dancing(self):
        self.play_song_sckt = threading.Thread( target= self.nao.play_song)
        self.play_song_sckt.start()
        self.nao.dance()
        
 
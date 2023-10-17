from helper_chatGPT import *
from helper_models import *
from helper_param import *

import socket
import pickle
import threading
import requests
import struct
import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
rabbit_channel = connection.channel()
rabbit_channel.queue_declare(queue='py2_py3_queue')
rabbit_channel.queue_declare(queue='py3_py2_queue')

execution_complete = False
def on_response(ch, method, properties, body):
        global execution_complete
        execution_complete = True

rabbit_channel.basic_consume(queue='py2_py3_queue', on_message_callback=on_response, auto_ack=True)


try:
    while True:

        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            
            execution_complete = False
            msg = "wake_word_dewtected"
            rabbit_channel.basic_publish(exchange='', routing_key='py3_py2_queue', body=msg)

            while not execution_complete:
                pass

except KeyboardInterrupt:
    print("\n ----- Python 3 Interupted ------")
    
connection.close()
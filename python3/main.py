import struct
import pika

# Wake word detection -----------
import pvporcupine
import pyaudio
import os
import wave

pico_key = os.environ["PICOVOICE_API_KEY"]
porc_model_path_ppn = "../models/hello-kai_en_linux_v2_2_0.ppn"
#porcupine = pvporcupine.create(access_key=pico_key, keyword_paths=[porc_model_path_ppn], model_path= porc_model_path_pv)
porcupine = pvporcupine.create(access_key=pico_key, keyword_paths=[porc_model_path_ppn])

# Initialize PyAudio and open a stream
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
rabbit_channel_in = connection.channel()
rabbit_channel_out = connection.channel()

rabbit_channel_in.queue_declare(queue='py2_py3_queue')
rabbit_channel_out.queue_declare(queue='py3_py2_queue')

execution_complete = False
def on_response(ch, method, properties, body):
        global execution_complete
        print("done")
        execution_complete = True

rabbit_channel_in.basic_consume(queue='py2_py3_queue', on_message_callback=on_response, auto_ack=True)

print("Start")
try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print("Wake Word detected")
            execution_complete = False
            msg = "wake_word_dewtected"
            rabbit_channel_out.basic_publish(exchange='', routing_key='py3_py2_queue', body=msg)


except KeyboardInterrupt:
    print("\n ----- Python 3 Interupted ------")
    
connection.close()
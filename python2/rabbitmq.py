
import pika
import threading 

connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
rabbit_channel_in = connection.channel()
rabbit_channel_in.queue_declare(queue='py3_py2_queue')

wake_word_detected = False
listening = True

def on_ping(ch, method, properties, body):
        global wake_word_detected, listening
        if listening:
            wake_word_detected = True
            print(" Wake word detected msg recived ")
        else:
            print("Not listening")

def start_listening():
    global listening, wake_word_detected
    wake_word_detected = False  
    listening = True
    print("----- Started Listening -----")
    
start_listening()

def stop_listening():
    global listening, wake_word_detected
    wake_word_detected = False
    listening = False

def is_wake_word_detected():
    global wake_word_detected
    if wake_word_detected:
      stop_listening()
      return True
    else:
      return False
      

def start_rabbitMQ():
    rabbit_channel_in.basic_consume(queue='py3_py2_queue', on_message_callback=on_ping, auto_ack=True)
    rabbit_channel_in.start_consuming()


# RabbitMQ thread
RabbitMQ_ISR = threading.Thread(target= start_rabbitMQ )
RabbitMQ_ISR.start()


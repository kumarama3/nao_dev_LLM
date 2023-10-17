from util import *
from helper import *
from helper_vision import *


# Initialise nao class
initialise_nao()

# Nao startup routine
nao_startup_routine()

# Attach nao's thread funtions
attach_thread_functions()

# Robot body Touch thread
Touch_ISR = threading.Thread(target= nao.initTG, args=(Touch_interrupts, nao, dance, play_song, led)  )
# Touch_ISR.start()

# Vision Threas
Vision_ISR = threading.Thread(target= nao_vision )
Vision_ISR.start()

end_time = time.time()

while True:
    server = False
    
    if wake_word_detected and (time.time() - end_time) > 4 :
        wake_word_detected = False

        nao.sayText_no_action("Hello")
        
        record_audio("audio/recording.wav", audio_clip_path, 5)
        
        start_time = time.time()
        try:
            response = requests.post(MAIN_API, data= {'user': AUDIO_AUTH_USER}  ,  files={'audio': open(audio_clip_path, 'rb') })
            if response.status_code == 200:
                    out = response.json()
                    for key, value in out.items():
                        print ( '{}\t : \t {}'.format(key, value) )
        except:
            print("Server Down")
        end_time = time.time()
        elapsed_time = end_time - start_time        
        print('\n Total Server Time taken: {:.4f} seconds'.format(elapsed_time))


        if not out['Auth']:
            
            nao.sayText( "You are not authorized user" ) 
            nao.posture.goToPosture("Stand" , 0.4)
            nao.ledStopListening()  

        else : 

            start_time = time.time()
            
            nao_do(out)
            
            elapsed_time = time.time() - start_time
            print('Total Time taken by robot : {:.4f} seconds'.format(elapsed_time))
        end_time = time.time()

        msg = "done"
        rabbit_channel.basic_publish(exchange='', routing_key='py2_py3_queue', body=msg)


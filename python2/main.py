from helper import *
from rabbitmq import *

# Initialise nao class
initialise_nao()

# Nao startup routine
nao_startup_routine()

# Attach nao's thread funtions
attach_thread_functions()

if TOUCH:
    # Robot body Touch thread
    Touch_ISR = threading.Thread(target= nao.initTG, args=(Touch_interrupts, nao, dance, play_song, led)  )
    Touch_ISR.start()

if VISION:
    from helper_vision import *
    
    Vision_ISR = threading.Thread(target= nao_vision )
    Vision_ISR.start()


end_time = time.time()

print(" Start Demo")

audio_path = "audio/recording.wav"

try:
    while True:
        
        if is_wake_word_detected():
            
            nao.sayText_no_action("Hello")
            
            record_audio(audio_path, 5)
            
            start_time = time.time()
            try:
                response = requests.post(MAIN_API, data= {'user': AUDIO_AUTH_USER , 'audio_auth' : AUDIO_AUTH }  ,  files={'audio': open(audio_path, 'rb')  })
                if response.status_code == 200:
                        out = response.json()
                        for key, value in out.items():
                            print ( '{}\t : \t {}'.format(key, value) )
            except:
                print("Server Down")
            end_time = time.time()
            elapsed_time = end_time - start_time        
            print('\n Total Server Time taken: {:.4f} seconds'.format(elapsed_time))

            try:

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
            
            except:
                print(" Issues with server")

            start_listening()

except KeyboardInterrupt:
    print("\n ----- Python 2 Interupted ------")
    
connection.close()

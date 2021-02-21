from RPi import GPIO
import time

debounceDelay=0.01

class HoopSensor:
    def __init__(self, m_signal, m_name, m_cb, m_obj):
        global debounceDelay
        self.signal = m_signal
        self.cbData = m_obj
        self.cb = m_cb
        self.dbDelay = debounceDelay
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.signal, GPIO.RISING,
                                callback=self.__dunkHandler,
                                bouncetime=200)

    def __dunkHandler(self, signal):
        time.sleep(0.05)
        if GPIO.input(signal):
            self.cb(self.cbData, signal, True)

    def cleanup(self):
        GPIO.cleanup() # cleanup all GPIO

# import keyboard
# import threading
# import time

# class HoopSensor:
#     def __init__(self, m_signal, m_cb):
#         self.signal = m_signal
#         self.cb = m_cb
#         self.dbDelay = 0.25
#         self.runIt = True
#         self.keythread = threading.Thread(target=self.__keyboardThread, args=(1,), daemon=True)
#         self.keythread.start()
#         #todo setup thread here

#     def __keyboardThread(self,name):
#         while self.runIt == True:
#             if keyboard.read_key() == self.signal:
#                 self.cb(self.signal)
#                 time.sleep(self.dbDelay)

#     def cleanup(self):
#         self.runIt = False
#         self.keythread.join()

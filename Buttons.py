from RPi import GPIO
import time

debounceDelay=0.01

class Button:
    def __init__(self, m_signal, m_name, m_cb, m_obj):
        global debounceDelay
        self.signal = m_signal
        self.cbData = m_obj
        self.cb = m_cb
        self.dbDelay = debounceDelay
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.signal, GPIO.BOTH,
                                callback=self.__pressHandler,
                                bouncetime=200)

    def __pressHandler(self, signal):
        time.sleep(0.05)
        if not (self.cb == None):
            self.cb(self.cbData, signal, GPIO.input(signal))

    def cleanup(self):
        GPIO.cleanup() # cleanup all GPIO

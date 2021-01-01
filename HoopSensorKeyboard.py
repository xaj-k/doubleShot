import keyboard
import threading
import time

class HoopSensor:
    def __init__(self, m_signal, m_cb):
        self.signal = m_signal
        self.cb = m_cb
        self.dbDelay = 0.25
        self.runIt = True
        self.keythread = threading.Thread(target=self.__keyboardThread, args=(1,), daemon=True)
        self.keythread.start()

    def __keyboardThread(self,name):
        while self.runIt == True:
            if keyboard.read_key() == self.signal:
                self.cb(self.signal)
                time.sleep(self.dbDelay)

    def cleanup(self):
        self.runIt = False
        self.keythread.join()
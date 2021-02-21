import keyboard
import threading
import time

class Button:
    def __init__(self, m_signal, m_name, m_cb, m_obj):
        self.signal = m_signal
        self.cbData = m_obj
        self.cb = m_cb
        self.dbDelay = 0.25
        self.runIt = True
        self.keythread = threading.Thread(target=self.__keyboardThread, args=(1,), daemon=True)
        self.keythread.start()
        #todo setup thread here

    def __keyboardThread(self, name):
        while self.runIt == True:
            if keyboard.read_key() == self.signal:
                self.cb(self.cbData, self.signal, False)
                time.sleep(self.dbDelay)

    def cleanup(self):
        self.runIt = False
        self.keythread.join()
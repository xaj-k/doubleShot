import keyboard
import threading
import time

class Button:
    def __init__(self, m_cb):
        self.cb = m_cb
        self.dbDelay = 0.25
        self.runIt = True
        self.keythread = threading.Thread(target=self.__keyboardThread, args=(1,), daemon=True)
        self.keythread.start()
        #todo setup thread here

    def __keyboardThread(self, name):
        while self.runIt == True:
            self.cb(keyboard.read_key())
            time.sleep(self.dbDelay)

    def cleanup(self):
        self.runIt = False
        self.keythread.join()
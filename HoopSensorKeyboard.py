import keyboard
import time

class HoopSensor:
    def __init__(self, m_signal, m_cb):
        self.key = m_signal
        self.cb = m_cb
        #todo setup thread here

    def __keyboardThread(self):
        while 1:
            if keyboard.read_key() == self.key:
                self.cb(self.key)

    def cleanup(self):
        # no need to do anything here
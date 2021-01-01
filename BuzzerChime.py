import pyaudio
import numpy as np
from scipy import signal

pobj = pyaudio.PyAudio()

class BuzzerChime():
    def __init__(self, volume, toneType, duration, frequency):
        self.volume = volume       # range [0.0, 1.0]
        self.duration = duration   # in seconds, may be float
        self.f = frequency         # Hz, may be float (e.g. 440.0)
        self.fs = 44100            # sampling rate, Hz, must be integer
        self.toneType = toneType   # options are 'sine', 'square', or 'sawtooth'
        self.__generateToneData()

    def __generateToneData(self):
         if self.toneType == 'sine':
             self.samples = (self.volume*np.sin(2 * np.pi * np.arange(self.fs*self.duration)*self.f/self.fs)).astype(np.float32).tobytes()
         elif self.toneType == 'square':
             self.samples = (self.volume*signal.square(2 * np.pi * np.arange(self.fs*self.duration)*self.f/self.fs)).astype(np.float32).tobytes()
         else:
             self.samples = (self.volume*signal.sawtooth(2 * np.pi * np.arange(self.fs*self.duration)*self.f/self.fs)).astype(np.float32).tobytes()

    def chime(self):
         global pobj
         stream = pobj.open(format=pyaudio.paFloat32,channels=1,rate=self.fs,output=True)
         stream.write(self.samples)
         stream.stop_stream()
         stream.close()

    def cleanup(self):
        pobj.terminate()

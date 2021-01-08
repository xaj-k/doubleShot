import tkinter as tk
from enum import Enum, auto
import random
import threading
import time
#import HoopSensor as hs
import HoopSensorKeyboard as hs
import BuzzerChime as bc
import Buttons as btn

#sudo apt-get install python3-all-dev portaudio19-dev
#pip3 install tk_tools RGpio keyboard numpy scipy pyaudio

## define globals/constants ##

# hoop signals
homeGPIO = 17
visitorGPIO = 27
homeKey = 'h'
visitorKey = 'v'
homeSignal = homeKey#homeGPIO
visitorSignal = visitorKey#visitorGPIO
# other
correctSignal = None
gameState = None
wrongbuzzer = None
rightbuzzer = None

## classes ##

class GameState(Enum):
    ANSWERING = auto()
    CORRECT = auto()
    INCORRECT = auto()

## functions ##

def showAnswer(signal):
    global hstr, vstr
    global homeSignal
    if signal == homeSignal:
        vstr = ' '
    else:
        hstr = ' '


def generateQuestion():
    global gameState
    global qstr, hstr, vstr
    global correctSignal,homeSignal,visitorSignal
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    qstr.set('%ix%i'%(a,b))
    if random.randint(0,1):
        hstr.set('%i'%(a*b))
        vstr.set('%i'%(a*b-3))
        correctSignal = homeSignal
    else:
        vstr.set('%i'%(a*b))
        hstr.set('%i'%(a*b+4))
        correctSignal = visitorSignal
    gameState = GameState.ANSWERING

def handleScore(signal):
    global correctSignal # if this doesn't work, use a get to return homeSignal/visitorSignal
    global gameState
    global wrongbuzzer
    if gameState == GameState.ANSWERING:
        if signal == correctSignal:
            print("correct!")
            gameState = GameState.CORRECT
            rightbuzzer.chime()
        else:
            print("wrong!")
            gameState = GameState.INCORRECT
            wrongbuzzer.chime()
        #showAnswer(signal)
        generateQuestion()

def graphicsThread(evt):
    while True:
        evt.wait()
        # do stuff
        #time.sleep(200) # todo use semaphores to signal this thread when game states change
        evt.clear()

## setup windows/widgets ##

root = tk.Tk()
root.title("Double Shot!")
# Create the main container
frame = tk.Frame(root, background='black')
# Lay out the main container, specify that we want it to grow with window size
frame.pack(fill=tk.BOTH, expand=True)
# labels for question, answers
qstr = tk.StringVar()
hstr = tk.StringVar()
vstr = tk.StringVar()
questionWidget = tk.Label(frame, textvariable=qstr, font=("Courier", 75), fg='red', bg='black')
homeWidget = tk.Label(frame, textvariable=hstr, font=("Courier", 100), fg='red', bg='black')
visitorWidget = tk.Label(frame, textvariable=vstr, font=("Courier", 100), fg='red', bg='black')
# place widgets
questionWidget.grid(row=0, column=1,sticky=tk.N)
homeWidget.grid(row=2, column=0,sticky=tk.SW)
visitorWidget.grid(row=2, column=2, sticky=tk.SE)

## setup hoop sensors ##

homeHoop = hs.HoopSensor(homeSignal, handleScore)
visitorHoop = hs.HoopSensor(visitorSignal, handleScore)
wrongbuzzer = bc.BuzzerChime(0.5, 'sawtooth', 0.25, 300)
rightbuzzer = bc.BuzzerChime(0.5, 'sine', 0.15, 600)

e = threading.Event()
gThread = threading.Thread(target=graphicsThread, args=(e,), daemon=True)
# use gThread.start() to start
# then use e.set() to set flag and e.clear() to e.clear() to clear

## initialize game variables ##

gameState = GameState.ANSWERING
generateQuestion()
try:
    root.mainloop()
    while 1:
        time.sleep(0.5)
except KeyboardInterrupt:
    homeHoop.cleanup()
    visitorHoop.cleanup()
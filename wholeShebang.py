import tkinter as tk
import tk_tools
import time
import HoopSensor as hs
#import HoopSensorKeyboard as hs
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
homeSignal = homeGPIO
visitorSignal = visitorGPIO
# game values
gameMode = None
# widget handles
gametimeDisplay = None
# other
fullscreen = False
root = None
keyScanner = None

## define classes ##

#class Chime():
#    def __init__(self):

class Team():
    global gameMode
    def __init__(self, m_root, m_timeKeeper, m_hoopSignal, m_freq):
        self.score = 0
        self.timeKeeper = m_timeKeeper
        self.ssWidget = tk_tools.SevenSegmentDigits(m_root, digits=2, background='black', digit_color='red', height=300)
        self.ssWidget.set_value(str(0))
        self.hoopSensor = hs.HoopSensor(m_hoopSignal, self.__handleScore)
        self.buzzer = bc.BuzzerChime(0.25, 'sine', 0.125, m_freq)

    def __handleScore(self, hoopSignal):
        if 1: #self.timeKeeper.getTime() > 0:
            if hoopSignal == self.hoopSensor.signal:
                self.addPoint(1)
                self.ssWidget.set_value(str(self.score))
                self.buzzer.chime() # todo have this called from a separate thread (set a semaphore to signal the thread to play it)

    def reset(self):
        self.score = 0
        self.ssWidget.set_value(str(self.score))

    def addPoint(self, points):
        self.score += 1
    
    def cleanup(self):
        self.reset()
        self.hoopSensor.cleanup()

class TimeKeeper():
    global gameMode
    def __init__(self, m_root, m_freq):
        self.ssWidget = tk_tools.SevenSegmentDigits(m_root, digits=2, background='black', digit_color='yellow', height=175)
        self.defaultTime = 30
        self.gameTime = 0
        self.root = m_root
        self.buzzer = bc.BuzzerChime(0.5, 'sawtooth', 1.5, m_freq)
        self.hurryBuzzer = bc.BuzzerChime(0.5, 'square', 0.25, m_freq)
        self.runIt = False
        #m_root.after(1000, self.__update_time)
        self.reset()

    def __update_time(self):
        if self.gameTime > 1 and self.runIt == True:
            self.gameTime -= 1
            if self.gameTime < 6:
                self.hurryBuzzer.chime()
            self.root.after(1000, self.__update_time)
        else:
            self.gameTime = 0
            self.runIt = False
            self.buzzer.chime()
        self.ssWidget.set_value(str(self.gameTime))

    def start(self, time):
        self.gameTime = time + 1
        if self.runIt == False:
            self.runIt = True
            self.__update_time()
        
    def getTime(self):
        return self.gameTime

    def reset(self):
        if self.runIt == False:
            self.start(self.defaultTime)
        else:
            self.gameTime = self.defaultTime
            self.ssWidget.set_value(str(self.gameTime))
    
    def cleanup(self):
        self.reset()
        self.runIt = False


## functions ##

def restartGame():
    timeKeeper.reset()
    homeTeam.reset()
    visitorTeam.reset()

def quit():
    global homeTeam
    global visitorTeam
    global keyScanner
    global timeKeeper
    visitorTeam.cleanup() # cleanup
    homeTeam.cleanup() # cleanup
    keyScanner.cleanup() # cleanup
    timeKeeper.cleanup()
    SystemExit()

def handleKeypress(key):
    global timeKeeper
    if key == 'r' or key == 'R':
        timeKeeper.start(30)
        homeTeam.reset()
        visitorTeam.reset()
    elif key == 'q' or key == 'Q':
        quit()

## setup windows/widgets ##

root = tk.Tk()
root.title("Double Shot!")
#root.attributes('-fullscreen', True)
# Create the main container
frame = tk.Frame(root, background='black')
# Lay out the main container, specify that we want it to grow with window size
frame.pack(fill=tk.BOTH, expand=True)
# Allow middle cell of grid to grow when window is resized
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)
# button containers
# frameb = tk.Frame(frame, background='grey')
# # Lay out the main container, specify that we want it to grow with window size
# frameb.pack(fill=tk.BOTH, expand=True)
# # Allow middle cell of grid to grow when window is resized
# frameb.columnconfigure(1, weight=1)
# frameb.rowconfigure(1, weight=1)

## setup timekeeper ##

timeKeeper = TimeKeeper(frame, 220)


## setup teams ##

homeTeam = Team(frame, timeKeeper, homeSignal, 440)
visitorTeam = Team(frame, timeKeeper, visitorSignal, 330)

## setup game buttons ##
reset_button = tk.Button(frame, text="Restart", command=restartGame)
fillerLabel = tk.Label(frame)


# place widgets
timeKeeper.ssWidget.grid(row=0, column=1)
homeTeam.ssWidget.grid(row=2, column=0)
visitorTeam.ssWidget.grid(row=2, column=2)
reset_button.grid(row=0, column=0)
reset_button.focus()

## setup buttons ##

keyScanner = btn.Button(handleKeypress)

##  main  ##

try:
    # todo call other setups
    
    #root.after(1000, timeKeeper.update_time())
    timeKeeper.start(30)
    root.mainloop()
    while 1:
        time.sleep(0.5)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    homeTeam.cleanup() # cleanup
    visitorTeam.cleanup() # cleanup

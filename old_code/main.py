import tkinter as tk
from enum import Enum, auto
import random
import threading
import time
import BuzzerChime as bc
import queue
import Buttons as btn
if 1:
    import HoopSensor as hs
else:
    import HoopSensorKeyboard as hs

#sudo apt-get install python3-all-dev portaudio19-dev
#pip3 install tk_tools RGpio keyboard numpy scipy pyaudio

## define globals/constants ##

# hoop signals
homeGPIO = 17
visitorGPIO = 27
homeKey = 'h'
visitorKey = 'v'
if 1:
    homeSignal = homeGPIO
    visitorSignal = visitorGPIO
else:
    homeSignal = homeKey
    visitorSignal = visitorKey
# other
defaultTime = 31
score = 0
isAddition = True
mMin = 2
mMax = 19
correctSignal = None
gameState = None
wrongbuzzer = None
rightbuzzer = None
uxEvent = None
gameTime = None

q = queue.Queue()

## classes ##

class GameState(Enum):
    ANSWERING = auto()
    CORRECT = auto()
    INCORRECT = auto()
    GAMEOVER = auto()
    IDLE = auto()

class GameEvent(Enum):
    TIMER_EXPIRED = auto()
    VISITOR_SCORED = auto()
    HOME_SCORED = auto()
    GAMETIME_UPDATED = auto()
    BUTTON_PRESSED = auto()
    BUTTON_HELD = auto()
    GAMESTATE_CHANGED = auto()

## functions ##

def showAnswer(signal):
    global hstr, vstr
    global homeSignal
    if signal == homeSignal:
        vstr.set('  ')
    else:
        hstr.set('  ')


def generateQuestion():
    global gameState
    global qstr, hstr, vstr
    global correctSignal,homeSignal,visitorSignal
    global mMin, mMax, isAddition

    a = random.randint(mMin, mMax)
    b = random.randint(mMin, mMax)
    if isAddition:
        qstr.set('%i+%i'%(a,b))
        answer = a+b
    else:
        qstr.set('%ix%i'%(a,b))
        answer = a*b
    if random.randint(0,1):
        hstr.set('%i'%(answer))
        if answer > 3:
            vstr.set('%i'%(answer-3))
        else:
            vstr.set('%i'%(answer+2))
        correctSignal = homeSignal
    else:
        vstr.set('%i'%(answer))
        hstr.set('%i'%(answer+4))
        correctSignal = visitorSignal
    gameState = GameState.ANSWERING

def restartGame():
    global gameState, gameTime
    global score, sVar, isAddition
    global mMin, mMax
    gameTime = defaultTime
    score = 0
    sVar.set(score)
    if isAddition == True:
        isAddition = False
        mMin = 2
        mMax = 9
    else:
        isAddition = True
        mMin = 2
        mMax = 19
    if gameState == GameState.GAMEOVER:
        gameState = GameState.ANSWERING
        generateQuestion()
        mTimer()

def handleScore(signal):
    global correctSignal # if this doesn't work, use a get to return homeSignal/visitorSignal
    global gameState
    global uxEvent
    global score, sVar
    if gameState == GameState.ANSWERING:
        if signal == correctSignal:
            gameState = GameState.CORRECT
            score += 1
            sVar.set(score)
        else:  
            gameState = GameState.INCORRECT
        uxEvent.set()
    else:
       restartGame() 

# events are queued via a circular buffer
# appropriate events are triggered by each sensor (buttons, timers, hoopSensors) based on the game state
# game states are only managed by main who consumes the events schuduled/queued in the circular buffer
# possible events are: homeScored, visitorScored, buttonPressed, buttonHeld, timerExpiried, gameStateChanged?
# e.g. if hoopsensor detects homeSignal AND gameState is answering, hoopsensor queues homeScored and sets eventSignal
#      mainthread gets event and handles homeScored event by checking that state is answering

if __name__ == "__main__":
    while True:
        event = q.get()
        if event == GameEvent.TIMER_EXPIRED:
            pass
        elif event == GameEvent.HOME_SCORED:
            if gameState == GameState.ANSWERING:
                if homeIsCorrect:
                    # pause time
                    # increment score
                    # update score display
                    # clear question/answer displays
                    # sound correct buzzer
                    # generate new question after 1 second and resume time
                    gameState = GameState.CORRECT
                else:
                    # pause time
                    # show answer
                    # sound wrong buzzer
                    # generate new question after 1 second and resume time
                    gameState = GameState.INCORRECT
            elif gameState == GameState.IDLE:
                # todo call start_new_game()
                    # note that new game will set gameState = GameState.ANSWERING
                    # generate a question based on button settings
                    # start the timer
                    # reset score to zero
                    # update all displays
                pass
        elif event == GameEvent.VISITOR_SCORED:
            # do same as HOME_SCORED except check if not homeIsCorrect
            pass
        elif event == GameEvent.BUTTON_PRESSED:
            pass
        
        # do stuf
        q.task_done()

        # handle game event accoring to state
        if gameState == GameState.ANSWERING:
            # update time display
            # update question/answers displays
        elif gameState == GameState.CORRECT:
            # pause time
            # update score display
            # show answer
            # sound correct buzzer
            # generate new question after 1 second and resume time
        elif gameState == GameState.INCORRECT:
            # pause time
            # show answer
            # sound wrong buzzer
            # generate new question after 1 second and resume time
        elif gameState == GameState.GAMEOVER:
            # update time display
            # update question/answers displays (clear them)
            # update score display
            # sound timesup buzzer
            # start gameover timer
            # set state to GameState.IDLE
        elif gameState == GameState.IDLE:
            # update score
            # update time
            # update operator
        # do stuff
        showAnswer(correctSignal)
        if gameState == GameState.GAMEOVER:
            continue
        elif gameState == GameState.CORRECT:
            print("correct!")
            gameTime = defaultTime
            rightbuzzer.chime()
        else:
            print("wrong!")
            wrongbuzzer.chime()
        time.sleep(1)
        generateQuestion()
        #time.sleep(200) # todo use semaphores to signal this thread when game states change
        evt.clear()

def changeTime():
    global defaultTime, gameTime, tVar, gameState
    gameState = GameState.GAMEOVER
    gameTime = 0
    if defaultTime == 61:
        defaultTime = 31
    elif defaultTime == 31:
        defaultTime = 16
    elif defaultTime == 16:
        defaultTime = 11
    elif defaultTime == 11:
        defaultTime = 6
    else:
        defaultTime = 61
    tVar.set(defaultTime-1)


def mTimer():
    global gameTime,  gameState, uxEvent, timesupbuzzer
    if gameTime > 1:
        gameTime -= 1
        root.after(1000, mTimer)
    else:
        gameTime = 0
        tVar.set(gameTime)
        gameState = GameState.GAMEOVER
        uxEvent.set()
        timesupbuzzer.chime()
    tVar.set(gameTime)

## setup windows/widgets ##

root = tk.Tk()
root.title("Double Shot!")
# Create the main container
frame = tk.Frame(root, background='black')
bframe = tk.Frame(frame, background='black')
# Lay out the main container, specify that we want it to grow with window size
frame.pack(fill=tk.BOTH, expand=True)
# Allow middle cell of grid to grow when window is resized
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)
# labels for question, answers
qstr = tk.StringVar()
hstr = tk.StringVar()
vstr = tk.StringVar()
tVar = tk.IntVar()
sVar = tk.IntVar()
questionWidget = tk.Label(frame, textvariable=qstr, font=("Courier", 100), fg='red', bg='black')
homeWidget = tk.Label(frame, textvariable=hstr, font=("Courier", 150), fg='red', bg='black')
visitorWidget = tk.Label(frame, textvariable=vstr, font=("Courier", 150), fg='red', bg='black')
timerWidget = tk.Label(frame, textvariable=tVar, font=("Courier", 60), fg='yellow', bg='black')
scoreWidget = tk.Label(frame, textvariable=sVar, font=("Courier", 45), fg='orange', bg='black')
reset_button = tk.Button(bframe, text="Restart", command=restartGame)
ctime_button = tk.Button(bframe, text="IncTime", command=changeTime)
# place widgets
questionWidget.grid(row=1, column=0, columnspan=3)
homeWidget.grid(row=2, column=0,sticky=tk.SE)
visitorWidget.grid(row=2, column=2, sticky=tk.SW)
timerWidget.grid(row=0,column=0)
scoreWidget.grid(row=0,column=2)
bframe.grid(row=2,column=1)
reset_button.pack()
ctime_button.pack()
reset_button.focus()
## setup hoop sensors ##

homeHoop = hs.HoopSensor(homeSignal, handleScore)
visitorHoop = hs.HoopSensor(visitorSignal, handleScore)
wrongbuzzer = bc.BuzzerChime(0.5, 'sawtooth', 0.25, 300)
rightbuzzer = bc.BuzzerChime(0.5, 'sine', 0.15, 600)
timesupbuzzer = bc.BuzzerChime(0.75, 'sawtooth', 1.25, 200)

uxEvent = threading.Event()
gThread = threading.Thread(target=graphicsThread, args=(uxEvent,), daemon=True)
# use gThread.start() to start
# then use e.set() to set flag and e.clear() to e.clear() to clear


# menu options

# gameoptions = ["Classic", "Multiplication", "Addition"]
# selected_gameoption = tk.StringVar()
# selected_gameoption.set(gameoptions[1])
# gameoptionmenu = tk.OptionMenu(root, selected_gameoption, *gameoptions)

# timeoptions = ["5", "10", "20", "30", "45", "60"]
# selected_timeoption = tk.StringVar()
# selected_timeoption.set(timeoptions[1])
# timeoptionmenu = tk.OptionMenu(root, selected_timeoption, *timeoptions)

## initialize game variables ##
gameState = GameState.ANSWERING
generateQuestion()
gThread.start()
gameTime = 15#defaultTime
mTimer()
try:
    root.mainloop()
    while 1:
        #gThread.join()
        # todo show score
        time.sleep(1)
        # start new game
        #gameState = GameState.ANSWERING
        #generateQuestion()
        #gThread.start()
        #gameTime = defaultTime
        #mTimer()
except KeyboardInterrupt:
    homeHoop.cleanup()
    visitorHoop.cleanup()
    gameState = GameState.GAMEOVER
    uxEvent.set()
    gThread.join()
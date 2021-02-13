import time
import queue, threading
import random
from sys import platform
from enum import Enum, auto

import Audio
import Graphics

if platform == "linux" or platform == "linux2":
    import HoopSensor as hs # use gpio
elif platform == "win32":
    import HoopSensorKeyboard as hs # use keyboard

# globals & constants
homeGPIO = 17
visitorGPIO = 27
homeKey = 'h'
visitorKey = 'v'

gameState = None
gameTime = None

homebuzzer = None
visitorbuzzer = None
hurryupbuzzer = None
gameoverbuzzer = None
correctbuzzer = None
wrongbuzzer = None

# classes
class GameState(Enum):
    ANSWERING = auto()
    CORRECT = auto()
    INCORRECT = auto()
    PAUSED = auto()
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

class BuzzerSelect(Enum):
    HOME_BUZZER = auto()
    VISITOR_BUZZER = auto()
    CORRECT_BUZZER = auto()
    WRONG_BUZZER = auto()
    HURRYUP_BUZZER = auto()
    GAMEOVER_BUZZER = auto()

class DoubleShotGameObj():
    def __init__(self, mhomesignal, mvisitorsignal):
        # game variables
        self.config = None
        #self.games = ["Classic", "Multiplication", "Addition"]
        self.gameState = GameState.IDLE
        self.gameTime = 0
        self.homeIsCorrect = True
        # timers
        self.gameTimer = None
        # buzzers
        self.homebuzzer = None
        self.visitorbuzzer = Buzzer(0.5, 'sine', 0.15, 600)
        self.hurryupbuzzer = None
        self.gameoverbuzzer = Buzzer(0.75, 'sawtooth', 1.25, 200)
        self.wrongbuzzer = Buzzer(0.5, 'sawtooth', 0.25, 300)
        # sensors
        self.homeHoop = hs.HoopSensor(mhomesignal, handleScoreEvent)
        self.visitorHoop = hs.HoopSensor(mvisitorsignal, handleScoreEvent)
        self.__homeSignal = mhomesignal
        self.__visitorSignal = mvisitorsignal
        # internal variables
        self.q = queue.Queue() # semaphore for injecting events into game state machine
        self.__blink = False
    def __receiveGameConfig(self, conf):
        self.gameConfig = conf #todo check config validity
    def startGame(self):
        self.gameUX.launch()
        pass

# functions

# todo have class constructor take 'name' as argument and keep array of buzzers and move this getter there

def getBuzzer(b):
    if b == BuzzerSelect.CORRECT_BUZZER:
        return correctbuzzer
    elif b == BuzzerSelect.WRONG_BUZZER:
        return wrongbuzzer
    elif b == BuzzerSelect.HOME_BUZZER:
        return homebuzzer
    elif b == BuzzerSelect.VISITOR_BUZZER:
        return visitorbuzzer
    elif b == BuzzerSelect.HURRYUP_BUZZER:
        return hurryupbuzzer
    elif b == BuzzerSelect.GAMEOVER_BUZZER:
        return gameoverbuzzer

# todo consider having handleXEvent for each gameType each in a respective file (e.g. multiplicationEventHandlers.py, classicEventHandlers.py, etc.)
def handleTimerEvent(gameObj):
    global gameState, gameTime
    if gameState == GameState.ANSWERING:
        # update time display
        Graphics.writeDisplay(DisplayType.TIME_DISPLAY,'%i'%gameTime)
        # if time less than hurryUpThreshold, sound hurryupbuzzer
        if gameTime > 0 and gameTime <= config.hurryupThreshold:
            getBuzzer(BuzzerSelect.HURRYUP_BUZZER).chime()
        # if time is zero, sound timesup buzzer and end the game
        else:
            gameState = GameState.GAMEOVER
            getBuzzer(BuzzerSelect.GAMEOVER_BUZZER).chime()
            gameObj.gameTimer = threading.Timer(config.limboPeriod, decGameTime) # stay in gameover state for 2 seconds
    elif gameState in [GameState.CORRECT, GameState.INCORRECT]:
        # reset gameTime
        gameTime = config.timeSet
        Graphics.writeDisplay(DisplayType.TIME_DISPLAY, '%i'%gameObj.gameTime)
        # generate new question
        a = random.randint(config.mathConfig.amin, config.mathConfig.amax)
        b = random.randint(config.mathConfig.bmin, config.mathConfig.bmax)
        if config.gameSelect == config.games.index("Multiplication"): # todo refactor to be a function something like get_abco(config)
            c = a*b
            op = 'x'
        else:
            c = a+b
            op = '+'
        if random.randint(0,1) and c > 2:
            w = c - random.randint(1, c-2)
        else:
            w = c + random.randint(2, 6)
        # update question/answer displays
        Graphics.writeDisplay(DisplayType.MESSAGE_DISPLAY,"%i %s %i = __"%(a,op,b))
        if random.randint(0,1):
            gameObj.homeIsCorrect = True
            Graphics.writeDisplay(DisplayType.HOME_DISPLAY,"%i"%c)
            Graphics.writeDisplay(DisplayType.VISITOR_DISPLAY,"%i"%w)
        else:
            gameObj.homeIsCorrect = False
            Graphics.writeDisplay(DisplayType.HOME_DISPLAY,"%i"%w)
            Graphics.writeDisplay(DisplayType.VISITOR_DISPLAY,"%i"%c)
        # update gameState to ANSWERING
        gameState = GameState.ANSWERING
    elif gameState == GameState.PAUSED:
        # toggle time display (timer)
        if gameObj.__blink == True:
            Graphics.writeDisplay(DisplayType.TIME_DISPLAY, ' ')
            gameObj.__blink = False
        else:
            Graphics.writeDisplay(DisplayType.TIME_DISPLAY, '%i'%gameObj.gameTime)
            gameObj.__blink = True
    elif gameState == GameState.GAMEOVER:
        # clear all displays
        gameObj.gameUX.clear_all_displays()
        # update gameState to IDLE
        gameState == GameState.IDLE

def decGameTime(self):
    if self.gameTime > 0:
        self.gameTime -= 1
        self.gameTimer = threading.Timer(1.0, self.decGameTime)
    self.q.put(GameEvent.GAMETIME_UPDATED)

def handleScoreEvent(gameObj, homeScored):
    global gameState
    if gameState == GameState.ANSWERING:
        if gameObj.gameSelect != gameObj.games.index("Classic"):
            if (homeScored and gameObj.homeIsCorrect) or (not homeScored and not gameObj.homeScored):
                # pause time
                if gameObj.gameTimer != None:
                    gameObj.gameTimer.cancel()
                gameObj.gameTimer = threading.Timer(0.25, gameObj.decGameTime)
                # increment score
                gameObj.homeScore += 1
                # update score display
                gameObj.urStringVar.set('%i' % gameObj.homeScore)
                # clear question/answer displays
                gameObj.messageStrVar.set(' ') # message display is middle row, column 0 with columnspan=3
                gameObj.hStrVar.set(' ')
                gameObj.vStrVar.set(' ')
                # update game state so that after brief delay we generate a new question and resume time
                gameState = GameState.CORRECT
                # sound correct buzzer
                getBuzzer(BuzzerSelect.rightbuzzer).chime()
            else:
                # pause time
                if gameObj.gameTimer != None:
                    gameObj.gameTimer.cancel()
                gameObj.gameTimer = threading.Timer(1.25, gameObj.decGameTime)
                # show answer
                if gameObj.homeIsCorrect:
                    gameObj.vStrVar.set(' ')
                else:
                    gameObj.hStrVar.set(' ')
                # generate new question after 1 second and resume time
                gameState = GameState.INCORRECT
                # sound wrong buzzer
                getBuzzer(BuzzerSelect.wrongbuzzer).chime()
        else: # game is classic
            if homeScored:
                # update score board
                gameObj.homeScore += 1
                gameObj.hStrVar.set('%i'%gameObj.homeScore)
                # sound the buzzer
                getBuzzer(BuzzerSelect.homebuzzer).chime()
            else:
                gameObj.visitorScore += 1
                gameObj.vStrVar.set('%i'%gameObj.visitorScore)
                # sound the buzzer
                getBuzzer(BuzzerSelect.visitorbuzzer).chime()
    elif gameState == GameState.IDLE:
        # todo start new game!
        pass

# functions

# setup variables

def __init__():
    gameState = GameState.IDLE
    gameTime = 30 #?? may not need this any more!

# main program
if __name__ == "__main__":
    if platform == "linux" or platform == "linux2":
        hSignal = homeGPIO
        vSignal = visitorGPIO
    elif platform == "win32":
        hSignal = homeKey
        vSignal = visitorKey
    try:
        game = DoubleShotGameObj(hSignal,vSignal)
        game.startGame()
        while True:
            event = game.q.get()
            if event == GameEvent.TIMER_EXPIRED:
                handleTimerEvent(game)
            elif event == GameEvent.HOME_SCORED:
                handleScoreEvent(game, True)
            elif event == GameEvent.VISITOR_SCORED:
                handleScoreEvent(game, False)
            elif event == GameEvent.BUTTON_PRESSED:
                pass
            # do stuf
            game.q.task_done()
    except KeyboardInterrupt:
        pass
        # todo clean up


# from tkinter import *

# lay=[]
# root = Tk()
# root.geometry('300x400+100+50')

# def create():
#   top = Toplevel()
#     
#     lay.append(top)

#     top.title("Main Panel")
#     top.geometry('500x500+100+450')
#     msg = Message(top, text="Show on Sub-panel",width=100)
#     msg.pack()

#     def exit_btn():

#         top.destroy()
#         top.update()

#     btn = Button(top,text='EXIT',command=exit_btn)
#     btn.pack()


# Button(root, text="Click me,Create a sub-panel", command=create).pack()
# mainloop()
       
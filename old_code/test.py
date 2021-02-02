import time
import queue, threading
import random
from sys import platform
from enum import Enum, auto
import Buzzer

if platform == "linux" or platform == "linux2":
    import HoopSensor as hs # use gpio
elif platform == "win32":
    import HoopSensorKeyboard as hs # use keyboard

# globals & constants
homeGPIO = 17
visitorGPIO = 27
homeKey = 'h'
visitorKey = 'v'

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

# todo consider moving ux objects to separate file


class DoubleShotGameObj():
    def __init__(self, mhomesignal, mvisitorsignal):
        # game variables
        self.games = ["Classic", "Multiplication", "Addition"]
        self.gameState = GameState.IDLE
        self.gameTime = 0
        # timers
        self.gameTimer = None
        # buzzers
        self.homebuzzer = None
        self.visitorbuzzer = bc.BuzzerChime(0.5, 'sine', 0.15, 600)
        self.hurryupbuzzer = None
        self.gameoverbuzzer = bc.BuzzerChime(0.75, 'sawtooth', 1.25, 200)
        self.wrongbuzzer = bc.BuzzerChime(0.5, 'sawtooth', 0.25, 300)
        # sensors
        self.homeHoop = hs.HoopSensor(mhomesignal, handleScoreEvent)
        self.visitorHoop = hs.HoopSensor(mvisitorsignal, handleScoreEvent)
        self.__homeSignal = mhomesignal
        self.__visitorSignal = mvisitorsignal
        # internal variables
        self.q = queue.Queue() # semaphore for injecting events into game state machine
        self.__blink = False
        # ux objects
        self.gameUX = DoubleShotUXObj()
        self.configUX = GameConfigUXObj(self.games, self.__receiveGameConfig)
        self.gameConfig = self.configUX.getConfig() # retrieve default config
        # other config items
        self.hurryUpThreshold = 5
        self.limboPeriod = 2.0
        self.mathConfig = MathConfig()
    def __receiveGameConfig(self, conf):
        self.gameConfig = conf #todo check config validity
    def startGame(self):
        self.gameUX.startIt()
        pass

# functions

# todo consider having handleXEvent for each gameType each in a respective file (e.g. multiplicationEventHandlers.py, classicEventHandlers.py, etc.)
def handleTimerEvent(gameObj):
    if gameObj.gameState == GameState.ANSWERING:
        # update time display
        gameObj.gameUX.write_display(DisplayType.TIME_DISPLAY,'%i'%gameObj.gameTime)
        # if time less than hurryUpThreshold, sound hurryupbuzzer
        if gameObj.gameTime > 0 and gameObj.gameTime <= gameObj.hurryUpThreshold:
            gameObj.hurryupbuzzer.chime()
        # if time is zero, sound timesup buzzer and end the game
        else:
            gameObj.gameState = GameState.GAMEOVER
            gameObj.gameoverbuzzer.chime()
            gameObj.gameTimer = threading.Timer(gameObj.limboPeriod, decGameTime) # stay in gameover state for 2 seconds
    elif gameObj.gameState in [GameState.CORRECT, GameState.INCORRECT]:
        # reset gameTime
        gameObj.gameTime = gameObj.gameConfig.timeSet
        gameObj.gameUX.write_display(DisplayType.TIME_DISPLAY, '%i'%gameObj.gameTime)
        # generate new question
        a = random.randint(gameObj.mathConfig.amin, gameObj.mathConfig.amax)
        b = random.randint(gameObj.mathConfig.bmin, gameObj.mathConfig.bmax)
        if gameObj.gameConfig.gameSelect == gameObj.games.index("Multiplication"):
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
        gameObj.gameUX.write_display(DisplayType.MESSAGE_DISPLAY,"%i %s %i = __"%(a,op,b))
        if random.randint(0,1):
            gameObj.homeIsCorrect = True
            gameObj.gameUX.write_display(DisplayType.HOME_DISPLAY,"%i"%c)
            gameObj.gameUX.write_display(DisplayType.VISITOR_DISPLAY,"%i"%w)
        else:
            gameObj.homeIsCorrect = False
            gameObj.gameUX.write_display(DisplayType.HOME_DISPLAY,"%i"%w)
            gameObj.gameUX.write_display(DisplayType.VISITOR_DISPLAY,"%i"%c)
        # update gameState to ANSWERING
        gameObj.gameState = GameState.ANSWERING
    elif gameObj.gameState == GameState.PAUSED:
        # toggle time display (timer)
        if gameObj.__blink == True:
            gameObj.gameUX.write_display(DisplayType.TIME_DISPLAY, ' ')
            gameObj.__blink = False
        else:
            gameObj.gameUX.write_display(DisplayType.TIME_DISPLAY, '%i'%gameObj.gameTime)
            gameObj.__blink = True
    elif gameObj.gameState == GameState.GAMEOVER:
        # clear all displays
        gameObj.gameUX.clear_all_displays()
        # update gameState to IDLE
        gameObj.gameState == GameState.IDLE

def decGameTime(self):
    if self.gameTime > 0:
        self.gameTime -= 1
        self.gameTimer = threading.Timer(1.0, self.decGameTime)
    self.q.put(GameEvent.GAMETIME_UPDATED)

def handleScoreEvent(gameObj, homeScored):
    if gameObj.gameState == GameState.ANSWERING:
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
                gameObj.gameState = GameState.CORRECT
                # sound correct buzzer
                gameObj.rightbuzzer.chime()
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
                gameObj.gameState = GameState.INCORRECT
                # sound wrong buzzer
                gameObj.wrongbuzzer.chime()
        else: # game is classic
            if homeScored:
                # update score board
                gameObj.homeScore += 1
                gameObj.hStrVar.set('%i'%gameObj.homeScore)
                # sound the buzzer
                gameObj.homebuzzer.chime()
            else:
                gameObj.visitorScore += 1
                gameObj.vStrVar.set('%i'%gameObj.visitorScore)
                # sound the buzzer
                gameObj.visitorbuzzer.chime()
    elif gameObj.gameState == GameState.IDLE:
        # todo start new game!
        pass

# functions

# setup variables


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
       
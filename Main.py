import time
import queue, threading
import random
import subprocess
from sys import platform
from enum import Enum, auto

import Audio
import Graphics

if platform == "linux" or platform == "linux2":
    import HoopSensor as hs # use gpio
    import Buttons
elif platform == "win32":
    import HoopSensorKeyboard as hs # use keyboard
    import ButtonsKeyboard as Buttons

# globals & constants

homeGPIO = 27
visitorGPIO = 17
powerGPIO = 3
playGPIO = 4
upGPIO = 2
downGPIO = 22 

homeKey = 'h'
visitorKey = 'v'
powerKey = 'p'
playKey = 's'
upKey = 'u'
downKey = 'd'

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
    def __init__(self, mhomesignal, mvisitorsignal, mbuttons, startCB):
        global homebuzzer, visitorbuzzer, hurryupbuzzer, gameoverbuzzer, correctbuzzer, wrongbuzzer
        # config
        self.config = None
        # game variables
        self.gameState = GameState.IDLE
        self.gameTime = 0
        self.homeIsCorrect = True
        # timers
        self.gameTimer = None
        # buzzers
        homebuzzer = Audio.Buzzer(0.5, 'sine', 0.15, 800)
        visitorbuzzer = Audio.Buzzer(0.5, 'sine', 0.15, 600)
        hurryupbuzzer = Audio.Buzzer(0.25, 'sine', 0.15, 440)
        gameoverbuzzer = Audio.Buzzer(0.75, 'sawtooth', 1.25, 200)
        correctbuzzer = Audio.Buzzer(0.5, 'sine', 0.15, 880)
        wrongbuzzer = Audio.Buzzer(0.5, 'sawtooth', 0.3, 200)
        # sensors
        self.homeHoop = hs.HoopSensor(mhomesignal, "home", handleSignal, self)
        self.visitorHoop = hs.HoopSensor(mvisitorsignal, "visitor", handleSignal, self)
        self.pwrBtn = Buttons.Button(mbuttons["power/mute"], "power/mute", handleSignal, self)
        self.playBtn = Buttons.Button(mbuttons["play"], "play", handleSignal, self)
        self.upBtn = Buttons.Button(mbuttons["up/pause"], "up/pause", handleSignal, self)
        self.dwnBtn = Buttons.Button(mbuttons["down/reset"], "down/reset", handleSignal, self)
        self.signals = {"home":mhomesignal, "visitor":mvisitorsignal}#, "power/mute":mpowermutesignal, "play":mplaysignal, "up/pause":muppausesignal, "down/reset":mdownresetsignal}
        self.signals.update(mbuttons)
        # internal variables
        self.q = queue.Queue() # semaphore for injecting events into game state machine
        self.__blink = False
        self.buttonHeld = True
        self.currentButton = None
        self.buttonHoldTime = 0
        self.buttonTimer = None
        # other configs
        self.limboPeriod = 3
        # callbacks
        self.startCB = startCB
    def receiveGameConfig(self, conf):
        self.config = conf #todo check config validity
        self.startCB(self)

# functions

def handleButtonHold(gameObj):
    if gameObj.currentButton == gameObj.signals["power/mute"] and gameObj.buttonHoldTime > 25:
        subprocess.call("init 0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pass # todo shutdown system here!
    # if gameObj.gameState == GameState.IDLE:
    #     if gameObj.uxSelect != "start": # todo figure this out
    #         if gameObj.currentButton == gameObj.signals["play"] and int(gameObj.buttonHoldTime*10) % 5 == 0:
    #             pass # todo call inc time set or something like that here

def incBtnTime(gameObj):
    if gameObj.buttonHeld == True:
        gameObj.buttonHoldTime += 0.1
        gameObj.buttonTimer = threading.Timer(0.1, incBtnTime, [gameObj])
        #gameObj.buttonTimer.start()
        handleButtonHold(gameObj)

def handleButtonEvent(gameObj, btn, btnState):
    if btnState == False: # button being pressed
        if gameObj.buttonHeld == False:
            gameObj.buttonHeld = True
            gameObj.currentButton = btn
            gameObj.buttonHoldTime = 0
            gameObj.buttonTimer = threading.Timer(0.1, incBtnTime, [gameObj])
            gameObj.buttonTimer.start()
        if btn == gameObj.signals["power/mute"]:
            subprocess.call("init 0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # todo toggle audio mute here!
            pass
        elif gameObj.gameState == GameState.IDLE:
            if btn == gameObj.signals["play"]:
                Graphics.clickButton()
            elif btn == gameObj.signals["up/pause"]:
                Graphics.nextButton()
            elif btn == gameObj.signals["down/reset"]:
                Graphics.previousButton()
    else:
        gameObj.buttonHeld = False
        if gameObj.buttonTimer != None:
            gameObj.buttonTimer.cancel()
    
def handleSignal(gameObj, signal, signalState):
    if signal == gameObj.signals["home"]:
        handleScoreEvent(gameObj, True)
    elif signal == gameObj.signals["visitor"]:
        handleScoreEvent(gameObj, False)
    elif signal == gameObj.signals["power/mute"] or signal == gameObj.signals["play"] or signal == gameObj.signals["up/pause"] or signal == gameObj.signals["down/reset"]:
        handleButtonEvent(gameObj, signal, signalState)
    
# todo have class constructor take 'name' as argument and keep array of buzzers and move this getter there

def getBuzzer(b):
    global homebuzzer, visitorbuzzer, hurryupbuzzer, gameoverbuzzer, correctbuzzer, wrongbuzzer
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

def generateQuestion(gameObj):
    # generate new question
    a = random.randint(gameObj.config.mathConfig.amin, gameObj.config.mathConfig.amax)
    b = random.randint(gameObj.config.mathConfig.bmin, gameObj.config.mathConfig.bmax)
    if gameObj.config.gameSelect == gameObj.config.games.index("Multiplication"): # todo refactor to be a function something like get_abco(config)
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
    Graphics.writeDisplay(Graphics.DisplayType.MESSAGE_DISPLAY,"%i %s %i"%(a,op,b))
    if random.randint(0,1):
        gameObj.homeIsCorrect = True
        Graphics.writeDisplay(Graphics.DisplayType.HOME_DISPLAY,"%i"%c)
        Graphics.writeDisplay(Graphics.DisplayType.VISITOR_DISPLAY,"%i"%w)
    else:
        gameObj.homeIsCorrect = False
        Graphics.writeDisplay(Graphics.DisplayType.HOME_DISPLAY,"%i"%w)
        Graphics.writeDisplay(Graphics.DisplayType.VISITOR_DISPLAY,"%i"%c)

# todo consider having handleXEvent for each gameType each in a respective file (e.g. multiplicationEventHandlers.py, classicEventHandlers.py, etc.)
def handleTimerEvent(gameObj):
    if gameObj.gameState == GameState.ANSWERING:
        # update time display
        Graphics.writeDisplay(Graphics.DisplayType.TIME_DISPLAY,'%i'%gameObj.gameTime)
        # if time less than hurryUpThreshold, sound hurryupbuzzer
        if gameObj.gameTime > 0 and gameObj.gameTime <= gameObj.config.hurryupThreshold:
            getBuzzer(BuzzerSelect.HURRYUP_BUZZER).chime()
        # if time is zero, sound timesup buzzer and end the game
        elif gameObj.gameTime == 0:
            gameObj.gameState = GameState.GAMEOVER
            getBuzzer(BuzzerSelect.GAMEOVER_BUZZER).chime()
            gameObj.gameTimer = threading.Timer(gameObj.limboPeriod, decGameTime, [gameObj]) # stay in gameover state for 2 seconds
            gameObj.gameTimer.start()
    elif gameObj.gameState == GameState.CORRECT or gameObj.gameState == GameState.INCORRECT:
        if gameObj.gameState == GameState.CORRECT:
            # reset gameTime
            gameObj.gameTime = gameObj.config.timeSet
        Graphics.writeDisplay(Graphics.DisplayType.TIME_DISPLAY, '%i'%gameObj.gameTime) # todo, move this to the to of this function and remove others
        generateQuestion(gameObj)
        # update gameState to ANSWERING
        gameObj.gameState = GameState.ANSWERING
    elif gameObj.gameState == GameState.PAUSED:
        # toggle time display (timer)
        if gameObj.__blink == True:
            Graphics.writeDisplay(Graphics.DisplayType.TIME_DISPLAY, ' ')
            gameObj.__blink = False
        else:
            Graphics.writeDisplay(Graphics.DisplayType.TIME_DISPLAY, '%i'%gameObj.gameTime)
            gameObj.__blink = True
    elif gameObj.gameState == GameState.GAMEOVER:
        # clear all displays
        # show config window
        # update gameState to IDLE
        gameObj.gameState = GameState.IDLE
        Graphics.showWindow(Graphics.WindowType.CONFIG_WINDOW) # begin by showing the config window

def decGameTime(gameObj):
    if gameObj.gameTime > 0:
        gameObj.gameTime -= 1
        gameObj.gameTimer = threading.Timer(1.0, decGameTime, [gameObj])
        gameObj.gameTimer.start()
    gameObj.q.put(GameEvent.GAMETIME_UPDATED)

def handleScoreEvent(gameObj, homeScored):
    if gameObj.gameState == GameState.ANSWERING:
        if gameObj.config.gameSelect != gameObj.config.games.index("Classic"):
            if (homeScored and gameObj.homeIsCorrect) or (not homeScored and not gameObj.homeIsCorrect):
                # pause time
                if gameObj.gameTimer != None:
                    gameObj.gameTimer.cancel()
                gameObj.gameTime = gameObj.config.timeSet # todo may not need this here
                gameObj.gameTimer = threading.Timer(0.25, decGameTime, [gameObj])
                gameObj.gameTimer.start()
                # increment score
                gameObj.homeScore += 1 # we only need to track one players score, so only use homeScore
                # update score display
                Graphics.writeDisplay(Graphics.DisplayType.SCORE_DISPLAY, '%i' % gameObj.homeScore)
                # clear question/answer displays
                Graphics.writeDisplay(Graphics.DisplayType.MESSAGE_DISPLAY, ' ')
                Graphics.writeDisplay(Graphics.DisplayType.HOME_DISPLAY,' ')
                Graphics.writeDisplay(Graphics.DisplayType.VISITOR_DISPLAY,' ')
                # update game state so that after brief delay we generate a new question and resume time
                gameObj.gameState = GameState.CORRECT
                # sound correct buzzer
                getBuzzer(BuzzerSelect.CORRECT_BUZZER).chime()
            else:
                # pause time
                if gameObj.gameTimer != None:
                    gameObj.gameTimer.cancel()
                gameObj.gameTimer = threading.Timer(1.25, decGameTime, [gameObj])
                gameObj.gameTimer.start()
                # show answer
                if gameObj.homeIsCorrect:
                    Graphics.writeDisplay(Graphics.DisplayType.VISITOR_DISPLAY,' ')
                else:
                    Graphics.writeDisplay(Graphics.DisplayType.HOME_DISPLAY,' ')
                # generate new question after 1 second and resume time
                gameObj.gameState = GameState.INCORRECT
                # sound wrong buzzer
                getBuzzer(BuzzerSelect.WRONG_BUZZER).chime()
        else: # game is classic
            if homeScored:
                # update score board
                gameObj.homeScore += 1
                Graphics.writeDisplay(Graphics.DisplayType.HOME_DISPLAY,'%i'%gameObj.homeScore)
                # sound the buzzer
                getBuzzer(BuzzerSelect.HOME_BUZZER).chime()
            else:
                gameObj.visitorScore += 1
                Graphics.writeDisplay(Graphics.DisplayType.VISITOR_DISPLAY,'%i'%gameObj.visitorScore)
                # sound the buzzer
                getBuzzer(BuzzerSelect.VISITOR_BUZZER).chime()
    elif gameObj.gameState == GameState.IDLE:
        # todo start new game!
        pass

def startGame(gameObj):
    gameObj.homeScore = 0
    gameObj.visitorScore = 0
    Graphics.writeDisplay(Graphics.DisplayType.HOME_DISPLAY,str(gameObj.homeScore))
    Graphics.writeDisplay(Graphics.DisplayType.VISITOR_DISPLAY,str(gameObj.visitorScore))
    Graphics.writeDisplay(Graphics.DisplayType.TIME_DISPLAY, str(gameObj.config.timeSet))
    if gameObj.config.gameSelect == gameObj.config.games.index("Classic"):
        gameObj.gameState = GameState.ANSWERING # this state will update time display on a time event
        Graphics.showWindow(Graphics.WindowType.CLASSIC_WINDOW) # show game window
    elif gameObj.config.gameSelect in [gameObj.config.games.index("Multiplication"), gameObj.config.games.index("Addition")]:
        Graphics.writeDisplay(Graphics.DisplayType.SCORE_DISPLAY,str(gameObj.homeScore))
        gameObj.gameState = GameState.CORRECT # this state will generate a new question on a time event
        Graphics.showWindow(Graphics.WindowType.MATH_WINDOW) # show game window
    gameObj.gameTime = gameObj.config.timeSet
    gameObj.gameTimer = threading.Timer(1.01, decGameTime, [gameObj]) # todo, instead of this do the q.put (otherwise there will be a delay??)
    # todo sound the gameBegin buzzer here
    #gameObj.q.put(GameEvent.GAMETIME_UPDATED)
    gameObj.gameTimer.start()

def gameEventListener(gameObj):
   while True:
        event = gameObj.q.get()
        if event == GameEvent.GAMETIME_UPDATED:
            handleTimerEvent(gameObj)
        elif event == GameEvent.HOME_SCORED:
            handleScoreEvent(gameObj, True)
        elif event == GameEvent.VISITOR_SCORED:
            handleScoreEvent(gameObj, False)
        elif event == GameEvent.BUTTON_PRESSED:
            pass
        # do stuf
        gameObj.q.task_done()

# main program
if __name__ == "__main__":
    if platform == "linux" or platform == "linux2":
        hSignal = homeGPIO
        vSignal = visitorGPIO
        btns = {"power/mute":powerGPIO, "play":playGPIO, "up/pause":upGPIO, "down/reset":downGPIO}
    elif platform == "win32":
        hSignal = homeKey
        vSignal = visitorKey
        btns = {"power/mute":powerKey, "play":playKey, "up/pause":upKey, "down/reset":downKey}
    try:
        game = DoubleShotGameObj(hSignal, vSignal, btns, startGame)
        x = threading.Thread(target=gameEventListener, args=(game,))
        x.start()
        Graphics.init(["Classic", "Multiplication", "Addition"], game.receiveGameConfig) # todo this may need to run on its own thread
        
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
       
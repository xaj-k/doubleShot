import tkinter as tk
import threading
from enum import Enum, auto
from functools import partial

# xdpyinfo | grep 'dimensions:'
#       1280 x 1024

class DisplayType(Enum):
    HOME_DISPLAY = auto()
    VISITOR_DISPLAY = auto()
    TIME_DISPLAY = auto()
    SCORE_DISPLAY = auto()
    MESSAGE_DISPLAY = auto()

class WindowType(Enum):
    CONFIG_WINDOW = auto()
    CLASSIC_WINDOW = auto()
    MATH_WINDOW = auto()

class MathConfig():
    def __init__(self):
        self.amin = 2
        self.amax = 9
        self.bmin = 6
        self.bmax = 9

class GameConfig():
    def __init__(self, games):
        self.startDelay = 4
        self.timeSet = 30 # todo change this to defaultTime
        self.hurryupThreshold = 5
        self.limboPeriod = 2
        self.gameSelect = 0
        self.volumeSet = 75
        self.games = games
        self.mathConfig = MathConfig()

## globals ##
# frames
_classicGameFrame = None # todo instead of global, have a getter that takes WindowType and returns frame handle
_mathGameFrame = None # todo instead of global, have a getter that takes WindowType and returns frame handle
_configFrame = None # todo instead of global, have a getter that takes WindowType and returns frame handle
_countdownFrame = None # todo instead of global, have a getter that takes WindowType and returns frame handle
# label variables
_hStrVar = None # home string variable
_vStrVar = None # visitor string variable
_sStrVar = None # score string variable
_tStrVar = None # time string variable
_mStrVar = None # message string variable
# buttons for software to use
_btnSel = None
_btns = []
# configs
_config = None

####### Functions ########

# callback for widgets
# from functools import partial
# button = Tk.Button(master=frame, text='press', command=partial(action, arg))

def __countDown__(f, var, cb):# todo: consider using Toplevel so _countDownFrame does not need to be managed outside this function
    global _config
    if var.get() > 1:
        f.tkraise()
        var.set(var.get()-1)
        threading.Timer(1, __countDown__, [f, var, cb]).start()
    else:
        #var.set(_config.startDelay)
        cb(_config)

def __incTime__(inc, var):
    global _config
    if _config.timeSet <= 55 and inc == True:
        _config.timeSet += 5
    elif _config.timeSet >= 10 and inc == False:
        _config.timeSet -= 5
    var.set(_config.timeSet)

def __selectNextGame__(var):
    global _config
    _config.gameSelect += 1
    if _config.gameSelect >= len(_config.games):
        _config.gameSelect = 0
    print(_config.gameSelect)
    print(_config.games[_config.gameSelect])
    print(len(_config.games))
    var.set(_config.games[_config.gameSelect])

def __updateButtons__():
    global _btnSel, _btns
    for b in _btns:
        b.config(borderwidth=1)
    _btns[_btnSel].config(borderwidth=10)

# startCB must take GameConfig() class as input argument
def init(games, startCB):
    global _config, _classicGameFrame, _mathGameFrame, _configFrame, _countdownFrame, _hStrVar, _vStrVar, _sStrVar, _tStrVar, _mStrVar, _btns, _btnSel

    _config = GameConfig(games)
    root = tk.Tk()
    root.title("Double Shot!")
    root.geometry('1280x1024')
    root.attributes('-fullscreen',True)
    # todo set fullscreen here
    # create the various windows
    _classicGameFrame = tk.Frame(root, background='black')
    _mathGameFrame = tk.Frame(root, background='black')
    _configFrame = tk.Frame(root, background='black') # todo specify size here
    _countdownFrame = tk.Frame(root, background='black') # todo specify size here
    # place the windows over top of eachother (only one will show at any given time)
    _classicGameFrame.grid(row=0, column=0, sticky="nsew")
    _mathGameFrame.grid(row=0, column=0, sticky="nsew")
    _configFrame.grid(row=0, column=0, sticky="nsew")
    _countdownFrame.grid(row=0, column=0, sticky="nsew")
    # create display variables for displaying graphics as part of the UX
    _hStrVar = tk.StringVar() # home string variable
    _vStrVar = tk.StringVar() # visitor string variable
    _sStrVar = tk.StringVar() # score string variable
    _tStrVar = tk.StringVar() # time string variable
    _mStrVar = tk.StringVar() # message string variable
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.grid_propagate(0)
    ## init countdown display ##
    countDownVar = tk.IntVar()
    countDownVar.set(_config.startDelay)
    tk.Label(_countdownFrame, textvariable=countDownVar, font=("Courier", 200), fg='red', bg='black').pack(pady=200)
    ## init config display ##
    # place holder to shift all buttons right
    tk.Label(_configFrame, bg='black', width=50).grid(row=0,column=0)
    # start button
    _startButton = tk.Button(_configFrame, text="Start", width=8, bg='black', fg='red', font=("Courier", 20), command=partial(__countDown__, _countdownFrame, countDownVar, startCB))
    _startButton.grid(row=0, rowspan=2, column=1, pady=(200,10))
    _btns.append(_startButton)
    # gameselect variable, buttons and label
    _gameSelectStringVar = tk.StringVar()
    _gameSelectStringVar.set(_config.games[_config.gameSelect])
    tk.Label(_configFrame, textvariable=_gameSelectStringVar, bg='black', fg='red', width=20, borderwidth=3, relief="ridge", font=("Courier", 20)).grid(row=2, column=2, rowspan=2) # label for configuring game
    _gameSelectButton = tk.Button(_configFrame, text=">", width=8, bg='black', fg='red', font=("Courier", 20), command=partial(__selectNextGame__, _gameSelectStringVar))
    _gameSelectButton.grid(row=2, column=1, rowspan=2, pady=10)
    _btns.append(_gameSelectButton)
    # timeset buttons/label
    _timeSetIntVar = tk.IntVar()
    _timeSetIntVar.set(_config.timeSet)
    tk.Label(_configFrame, textvariable=_timeSetIntVar, bg='black', fg='red', borderwidth=3, relief="ridge", width=20, font=("courier", 20)).grid(row=4, column=2, rowspan=2, pady=10)
    _timesetUpButton = tk.Button(_configFrame, text="+", width=16, bg='black', fg='red', font=("courier", 10), command=partial(__incTime__, True, _timeSetIntVar))
    _timesetDownButton = tk.Button(_configFrame, text="-", width=16, bg='black', fg='red', font=("courier", 10), command=partial(__incTime__, False, _timeSetIntVar))
    _timesetUpButton.grid(row=4, column=1, pady=(10,0))
    _timesetDownButton.grid(row=5 ,column=1)
    _btns.append(_timesetUpButton)
    _btns.append(_timesetDownButton)
     # start with 1st button selected and highlight selected button
    _btnSel = 0
    __updateButtons__()
    ## init game displays ##
    # labels widgets for classic
    tk.Label(_classicGameFrame, textvariable=_hStrVar, font=("Courier", 150), fg='red', bg='black').grid(row=1, column=2, padx=(10,200))
    tk.Label(_classicGameFrame, textvariable=_vStrVar, font=("Courier", 150), fg='red', bg='black').grid(row=1, column=0, padx=(200,10))
    tk.Label(_classicGameFrame, textvariable=_tStrVar, font=("Courier", 90), fg='red', bg='black').grid(row=0,column=1)
    _classicGameFrame.grid(sticky='nswe')
    _classicGameFrame.rowconfigure(0, weight=1)
    _classicGameFrame.columnconfigure(0, weight=1)
    _classicGameFrame.rowconfigure(1, weight=1)
    _classicGameFrame.columnconfigure(1, weight=1)
    _classicGameFrame.columnconfigure(2, weight=1)
    _classicGameFrame.grid_propagate(0)
    # labels widgets for math
    tk.Label(_mathGameFrame, textvariable=_hStrVar, width=4, font=("Courier", 150), fg='red', bg='black').grid(row=2, column=0, padx=(50,2))
    tk.Label(_mathGameFrame, textvariable=_vStrVar, width=4, font=("Courier", 150), fg='red', bg='black').grid(row=2, column=2, padx=(2,50))
    tk.Label(_mathGameFrame, textvariable=_tStrVar, width=4, font=("Courier", 60), fg='yellow', bg='black').grid(row=0,column=0)
    tk.Label(_mathGameFrame, textvariable=_mStrVar, width=16, font=("Courier", 100), fg='red', bg='black').grid(row=1, column=0, columnspan=3, padx=20)
    tk.Label(_mathGameFrame, textvariable=_sStrVar, width=4, font=("Courier", 45), fg='orange', bg='black').grid(row=0,column=2)
    _mathGameFrame.grid(sticky='nswe')
    _mathGameFrame.rowconfigure(0, weight=1)
    _mathGameFrame.columnconfigure(0, weight=1)
    _mathGameFrame.rowconfigure(1, weight=1)
    _mathGameFrame.columnconfigure(1, weight=1)
    _mathGameFrame.rowconfigure(2, weight=1)
    _mathGameFrame.columnconfigure(2, weight=1)
    _mathGameFrame.grid_propagate(0)
    # begin graphics
    showWindow(WindowType.CONFIG_WINDOW) # begin by showing the config window
    root.mainloop()

def clickButton():
    global _btnSel, _btns
    _btns[_btnSel].invoke()

def nextButton():
    global _btnSel, _btns
    _btnSel -= 1
    if _btnSel < 0:
        _btnSel = len(_btns)-1
    __updateButtons__()

def previousButton():
    global _btnSel, _btns
    _btnSel += 1
    if _btnSel >= len(_btns):
        _btnSel = 0
    __updateButtons__()

def showWindow(winSel):
    global _configFrame, _classicGameFrame, _mathGameFrame, _countDownFrame
    if winSel == WindowType.CONFIG_WINDOW:
        _configFrame.tkraise()
    elif winSel == WindowType.MATH_WINDOW:
        _mathGameFrame.tkraise()
    elif winSel == WindowType.CLASSIC_WINDOW:
        _classicGameFrame.tkraise()

def getConfig():
    return _config

def writeDisplay(displaySel, str):
    global _hStrVar, _vStrVar, _sStrVar, _tStrVar, _mStrVar
    # options are home, visitor, score, time, message
    if displaySel == DisplayType.HOME_DISPLAY:
        _hStrVar.set(str)
    elif displaySel == DisplayType.VISITOR_DISPLAY:
        _vStrVar.set(str)
    elif displaySel == DisplayType.TIME_DISPLAY:
        _tStrVar.set(str)
    elif displaySel == DisplayType.SCORE_DISPLAY:
        _sStrVar.set(str)
    elif displaySel == DisplayType.MESSAGE_DISPLAY:
        _mStrVar.set(str)

## for debugging ##
def mathTest(stuff):
    print("yay! you started it!")
    writeDisplay(DisplayType.HOME_DISPLAY, "HH")
    writeDisplay(DisplayType.VISITOR_DISPLAY, "VV")
    writeDisplay(DisplayType.TIME_DISPLAY, "TT")
    writeDisplay(DisplayType.SCORE_DISPLAY, "SS")
    writeDisplay(DisplayType.MESSAGE_DISPLAY, "This is math")
    showWindow(WindowType.MATH_WINDOW)

def classicTest(stuff):
    print("yay! you started it!")
    writeDisplay(DisplayType.HOME_DISPLAY, "HH")
    writeDisplay(DisplayType.VISITOR_DISPLAY, "VV")
    writeDisplay(DisplayType.TIME_DISPLAY, "TT")
    showWindow(WindowType.CLASSIC_WINDOW)

if __name__ == "__main__":
    init(["Classic", "Multiplication"], mathTest)
    pass
########################


''' ##### move to inside of larger init #####
# mFrame will be used to display pop-up messages and/or stats including high scores, player averages, etc.
def __initConfigAndMessageDisplays__(frame, cdFrame, mFrame):
    global _config, _startCallback

    # init countdown here for when start button is pressed
    _countDownVar = tk.IntVar()
    _countDownVar.set(_config.startDelay)
    tk.Label(cdFrame, textvariable=_countDownVar, font=("Courier", 200), fg='red', bg='black').pack()
    # gameselect buttons/label
    _gameSelectStringVar = tk.StringVar()
    _gameSelectStringVar.set(_config.games[_config.gameSelect])
    gameSelectFrame = tk.Frame(frame, background='black')
    gameSelectFrame.pack()
    tk.Label(gameSelectFrame, textvariable=_gameSelectStringVar).grid(row=0,column=0) # label for configuring game
    tk.Button(gameSelectFrame, text="+", command=partial(__selectNextGame__, _gameSelectStringVar)).grid(row=0,column=1)
    # timeset buttons/label
    _timeSetIntVar = tk.IntVar()
    _timeSetIntVar.set(_config.timeSet)
    timeSetFrame = tk.Frame(frame, background='black')
    timeSetFrame.pack()
    tk.Button(timeSetFrame, text="-", command=partial(__incTime__, False, _timeSetIntVar)).grid(row=0,column=0) # NOTE, to animate/highlight, you may need to store handle before placing on grid
    tk.Label(timeSetFrame, textvariable=_timeSetIntVar).grid(row=0,column=1)
    tk.Button(timeSetFrame, text="+", command=partial(__incTime__, True, _timeSetIntVar)).grid(row=0,column=2) # NOTE, to animate/highlight, you may need to store handle before placing on grid
    # start button
    tk.Button(frame, text="Start", command=partial(__countDown__, cdFrame, _countDownVar, _startCallback)).pack()

def __initClassicDisplay__(frame, hstr, vstr, tstr):
    # labels widgets
    tk.Label(frame, textvariable=hstr, font=("Courier", 150), fg='red', bg='black').grid(row=1, column=2, sticky=tk.SW) # todo check if sticky is correct
    tk.Label(frame, textvariable=vstr, font=("Courier", 150), fg='red', bg='black').grid(row=1, column=0, sticky=tk.SE) # todo check if sticky is correct
    tk.Label(frame, textvariable=tstr, font=("Courier", 90), fg='red', bg='black').grid(row=0,column=1)


def __initMathDisplay__(frame, hstr, vstr, tstr, sstr, mstr):
    # labels widgets
    tk.Label(frame, textvariable=hstr, font=("Courier", 150), fg='red', bg='black').grid(row=2, column=0,sticky=tk.SE)
    tk.Label(frame, textvariable=vstr, font=("Courier", 150), fg='red', bg='black').grid(row=2, column=2, sticky=tk.SW)
    tk.Label(frame, textvariable=sstr, font=("Courier", 60), fg='yellow', bg='black').grid(row=0,column=0)
    tk.Label(frame, textvariable=mstr, font=("Courier", 100), fg='red', bg='black').grid(row=1, column=0, columnspan=3)
    tk.Label(frame, textvariable=tstr, font=("Courier", 45), fg='orange', bg='black').grid(row=0,column=2)
##### end of move to inside of larger init ##### '''


# class GameConfigUXObj():
#     def __init__(self, games, startCallback):
#         self.gameConfig = GameConfig()
#         self.startCallback = startCallback
#         self.__games = games
#         self.__gameSelectStringVar = tk.StringVar()
#         self.__timeSetIntVar = tk.IntVar()
#         self.__top = tk.Toplevel()
#         self.__mainframe = tk.Frame(self.__top, background='black')
#         self.__buttonsFrame = tk.Frame(self.__mainframe, background='black')
#         self.__timeSetFrame = tk.Frame(self.__buttonsFrame, background='black')
#         self.__gameSelectFrame = tk.Frame(self.__buttonsFrame, background='black')
#         # setup labels
#         self.__gameSelectLabel = tk.Label(self.__gameSelectFrame,textvariable=self.__gameSelectStringVar) # label for configuring game
#         self.__timeSetLabel = tk.Label(self.__timeSetFrame, textvariable=self.__timeSetIntVar)
#         # buttons widgets
#         self.__startButton = tk.Button(self.__buttonsFrame, text="Start", command=self.__handleStartPress)
#         self.__gameSelectNext = tk.Button(self.__gameSelectFrame, text="+", command=self.selectNextGame)
#         self.__timeSetUp = tk.Button(self.__timeSetFrame, text="+", command=self.increaseTime)
#         self.__timeSetDown = tk.Button(self.__timeSetFrame, text="-", command=self.decreaseTime)
#         # set initial values for widget variables
#         self.__gameSelectStringVar.set(self.__games[self.gameConfig.gameSelect])
#         self.__timeSetIntVar.set(self.gameConfig.timeSet) # todo decide where to set the default time
#         self.layItout()
#     def __handleStartPress(self):
#         self.startCallback(self.gameConfig)  # signal to the user that start had been pressed and hand them the current game config
#         # todo close the top window
#         self.__top.destroy()
#         self.__top.update()
#     def getConfig(self):
#         return self.gameConfig
#     def layItout(self):
#         self.__top.title("Game Configure")
#         #self.__top.geometry('500x500+100+450')
#         self.__mainframe.pack()
#         self.__buttonsFrame.grid(row=0,column=1)
#         self.__gameSelectLabel.grid(row=0,column=0)
#         self.__gameSelectNext.grid(row=0,column=1)
#         self.__timeSetDown.grid(row=0,column=0)
#         self.__timeSetLabel.grid(row=0,column=1)
#         self.__timeSetUp.grid(row=0,column=2)
#         self.__gameSelectFrame.pack()
#         self.__timeSetFrame.pack()
#         self.__startButton.pack()
#         #self.__top.update()
#         print("Showing top")
#     def showGameConfigDisplay(self, showIt):
#         # this closes the top window, or creates a new one with currently set game configuration
#         pass
#     def decreaseTime(self):
#         curTime = self.__timeSetIntVar.get()
#         if curTime >= 10:
#             self.__timeSetIntVar.set(curTime -5)
#         pass
#     def increaseTime(self):
#         curTime = self.__timeSetIntVar.get()
#         if curTime <= 55:
#             self.__timeSetIntVar.set(curTime + 5)
#         pass
#     def selectNextGame(self):
#         self.gameConfig.gameSelect += 1
#         if self.gameConfig.gameSelect >= len(self.__games):
#             self.gameConfig.gameSelect = 0
#         self.__gameSelectStringVar.set(self.__games[self.gameConfig.gameSelect])
#         pass
#     def startGame(self):
#         # todo close gameConfigWindow, start game with current config settings
#         pass

# class DoubleShotUXObj():    
#     def __init__(self):
#         self.__root = tk.Tk()
#         #self.__root.attributes('-fullscreen', True)
#         # Create Frame Containers
#         self.__mainframe = tk.Frame(self.__root, background='black')
#         # variables for labels
#         self.__hStrVar = tk.StringVar() # lower left
#         self.__vStrVar = tk.StringVar() # lower right
#         self.__umStrVar = tk.StringVar() # upper middle
#         self.__sStrVar = tk.StringVar() # upper right
#         self.__tStrVar = tk.StringVar() # upper left
#         self.__mStrVar = tk.StringVar()  # center
#         # labels widgets
#         self.__vLabel = tk.Label(self.__mainframe, textvariable=self.__hStrVar, font=("Courier", 150), fg='red', bg='black')
#         self.__vLabel = tk.Label(self.__mainframe, textvariable=self.__vStrVar, font=("Courier", 150), fg='red', bg='black')
#         self.__sLabel = tk.Label(self.__mainframe, textvariable=self.__sStrVar, font=("Courier", 60), fg='yellow', bg='black')
#         self.__mLabel = tk.Label(self.__mainframe, textvariable=self.__mStrVar, font=("Courier", 100), fg='red', bg='black')
#         self.__tLabel = tk.Label(self.__mainframe, textvariable=self.__tStrVar, font=("Courier", 45), fg='orange', bg='black')
#         self.layItOut()
#     def layItOut(self):
#         # todo move most of the below to a ux_setup function
#         self.__root.title("Double Shot!")
#         # Lay out the main container, specify that we want it to grow with window size
#         self.__mainframe.pack(fill=tk.BOTH, expand=True)
#         # Allow middle cell of grid to grow when window is resized
#         self.__mainframe.columnconfigure(1, weight=1)
#         self.__mainframe.rowconfigure(1, weight=1)
#         # place widgets
#         self.__sLabel.grid(row=0,column=0)
#         self.__tLabel.grid(row=0,column=2) # todo this is dependent on the gameSelect
#         self.__mLabel.grid(row=1, column=0, columnspan=3)
#         self.__vLabel.grid(row=2, column=0,sticky=tk.SE)
#         self.__vLabel.grid(row=2, column=2, sticky=tk.SW)   
#         # TODO have public functions that enable user to update each display field
#     def countDown(self):
#         if countDownVar == None:
#             countDownVar = tk.IntVar()
#             countDownWindow = tk.Toplevel()
#             countDownLabel = tk.Label(countDownWindow,textvariable=countDownVar)
#             countDownLabel.pack()
#             countDownVar.set(3)
#         elif countDownVar.get() > 0:
#             countDownVar.set(countDownVar.get() - 1)
#         else:
#             countDownWindow.destroy()
#             countDownVar = None
#             # todo call startGame()
#             return
#         countDownWindow.after(1000, self.countDown)
#     def write_display(self, displaySel, str):
#         # options are home, visitor, score, time, message
#         if displaySel == DisplayType.HOME_DISPLAY:
#             self.__hStrVar.set(str)
#         elif displaySel == DisplayType.VISITOR_DISPLAY:
#             self.__vStrVar.set(str)
#         elif displaySel == DisplayType.TIME_DISPLAY:
#             self.__tStrVar.set(str)
#         elif displaySel == DisplayType.SCORE_DISPLAY:
#             self.__sStrVar.set(str)
#         elif displaySel == DisplayType.MESSAGE_DISPLAY:
#             self.__mStrVar.set(str)
#     def clear_all_displays(self):
#         for d in range(len(DisplayType)-1):
#             self.write_display(d, ' ')
#     def launch(self):
#         self.__root.mainloop() # todo where do I call this and can I call it more than once???
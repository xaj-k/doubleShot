import tkinter as tk
from enum import Enum, auto

class DisplayType(Enum):
    HOME_DISPLAY = auto()
    VISITOR_DISPLAY = auto()
    TIME_DISPLAY = auto()
    SCORE_DISPLAY = auto()
    MESSAGE_DISPLAY = auto()

class GameConfig():
    def __init__(self):
        self.timeSet = 30
        self.gameSelect = 0
        self.volumeSet = 75

class MathConfig():
    def __init__(self):
        self.amin = 2
        self.amax = 9
        self.bmin = 6
        self.bmax = 9

class GameConfigUXObj():
    def __init__(self, games, startCallback):
        self.gameConfig = GameConfig()
        self.startCallback = startCallback
        self.__games = games
        self.__gameSelectStringVar = tk.StringVar()
        self.__timeSetIntVar = tk.IntVar()
        self.__top = tk.Toplevel()
        self.__mainframe = tk.Frame(self.__top, background='black')
        self.__buttonsFrame = tk.Frame(self.__mainframe, background='black')
        self.__timeSetFrame = tk.Frame(self.__buttonsFrame, background='black')
        self.__gameSelectFrame = tk.Frame(self.__buttonsFrame, background='black')
        # setup labels
        self.__gameSelectLabel = tk.Label(self.__gameSelectFrame,textvariable=self.__gameSelectStringVar) # label for configuring game
        self.__timeSetLabel = tk.Label(self.__timeSetFrame, textvariable=self.__timeSetIntVar)
        # buttons widgets
        self.__startButton = tk.Button(self.__buttonsFrame, text="Start", command=self.__handleStartPress)
        self.__gameSelectNext = tk.Button(self.__gameSelectFrame, text="+", command=self.selectNextGame)
        self.__timeSetUp = tk.Button(self.__timeSetFrame, text="+", command=self.increaseTime)
        self.__timeSetDown = tk.Button(self.__timeSetFrame, text="-", command=self.decreaseTime)
        # set initial values for widget variables
        self.__gameSelectStringVar.set(self.__games[self.gameConfig.gameSelect])
        self.__timeSetIntVar.set(self.gameConfig.timeSet) # todo decide where to set the default time
        self.layItout()
    def __handleStartPress(self):
        self.startCallback(self.gameConfig)  # signal to the user that start had been pressed and hand them the current game config
        # todo close the top window
        self.__top.destroy()
        self.__top.update()
    def getConfig(self):
        return self.gameConfig
    def layItout(self):
        self.__top.title("Game Configure")
        #self.__top.geometry('500x500+100+450')
        self.__mainframe.pack()
        self.__buttonsFrame.grid(row=0,column=1)
        self.__gameSelectLabel.grid(row=0,column=0)
        self.__gameSelectNext.grid(row=0,column=1)
        self.__timeSetDown.grid(row=0,column=0)
        self.__timeSetLabel.grid(row=0,column=1)
        self.__timeSetUp.grid(row=0,column=2)
        self.__gameSelectFrame.pack()
        self.__timeSetFrame.pack()
        self.__startButton.pack()
        #self.__top.update()
        print("Showing top")
    def showGameConfigDisplay(self, showIt):
        # this closes the top window, or creates a new one with currently set game configuration
        pass
    def decreaseTime(self):
        curTime = self.__timeSetIntVar.get()
        if curTime >= 10:
            self.__timeSetIntVar.set(curTime -5)
        pass
    def increaseTime(self):
        curTime = self.__timeSetIntVar.get()
        if curTime <= 55:
            self.__timeSetIntVar.set(curTime + 5)
        pass
    def selectNextGame(self):
        self.gameConfig.gameSelect += 1
        if self.gameConfig.gameSelect >= len(self.__games):
            self.gameConfig.gameSelect = 0
        self.__gameSelectStringVar.set(self.__games[self.gameConfig.gameSelect])
        pass
    def startGame(self):
        # todo close gameConfigWindow, start game with current config settings
        pass

class DoubleShotUXObj():    
    def __init__(self):
        self.__root = tk.Tk()
        #self.__root.attributes('-fullscreen', True)
        # Create Frame Containers
        self.__mainframe = tk.Frame(self.__root, background='black')
        # variables for labels
        self.__hStrVar = tk.StringVar() # lower left
        self.__vStrVar = tk.StringVar() # lower right
        self.__umStrVar = tk.StringVar() # upper middle
        self.__sStrVar = tk.StringVar() # upper right
        self.__tStrVar = tk.StringVar() # upper left
        self.__mStrVar = tk.StringVar()  # center
        # labels widgets
        self.__vLabel = tk.Label(self.__mainframe, textvariable=self.__hStrVar, font=("Courier", 150), fg='red', bg='black')
        self.__vLabel = tk.Label(self.__mainframe, textvariable=self.__vStrVar, font=("Courier", 150), fg='red', bg='black')
        self.__sLabel = tk.Label(self.__mainframe, textvariable=self.__sStrVar, font=("Courier", 60), fg='yellow', bg='black')
        self.__mLabel = tk.Label(self.__mainframe, textvariable=self.__mStrVar, font=("Courier", 100), fg='red', bg='black')
        self.__tLabel = tk.Label(self.__mainframe, textvariable=self.__tStrVar, font=("Courier", 45), fg='orange', bg='black')
        self.layItOut()
    def layItOut(self):
        # todo move most of the below to a ux_setup function
        self.__root.title("Double Shot!")
        # Lay out the main container, specify that we want it to grow with window size
        self.__mainframe.pack(fill=tk.BOTH, expand=True)
        # Allow middle cell of grid to grow when window is resized
        self.__mainframe.columnconfigure(1, weight=1)
        self.__mainframe.rowconfigure(1, weight=1)
        # place widgets
        self.__sLabel.grid(row=0,column=0)
        self.__tLabel.grid(row=0,column=2) # todo this is dependent on the gameSelect
        self.__mLabel.grid(row=1, column=0, columnspan=3)
        self.__vLabel.grid(row=2, column=0,sticky=tk.SE)
        self.__vLabel.grid(row=2, column=2, sticky=tk.SW)   
        # TODO have public functions that enable user to update each display field
    def countDown(self):
        if countDownVar == None:
            countDownVar = tk.IntVar()
            countDownWindow = tk.Toplevel()
            countDownLabel = tk.Label(countDownWindow,textvariable=countDownVar)
            countDownLabel.pack()
            countDownVar.set(3)
        elif countDownVar.get() > 0:
            countDownVar.set(countDownVar.get() - 1)
        else:
            countDownWindow.destroy()
            countDownVar = None
            # todo call startGame()
            return
        countDownWindow.after(1000, self.countDown)
    def write_display(self, displaySel, str):
        # options are home, visitor, score, time, message
        if displaySel == DisplayType.HOME_DISPLAY:
            self.__hStrVar.set(str)
        elif displaySel == DisplayType.VISITOR_DISPLAY:
            self.__vStrVar.set(str)
        elif displaySel == DisplayType.TIME_DISPLAY:
            self.__tStrVar.set(str)
        elif displaySel == DisplayType.SCORE_DISPLAY:
            self.__sStrVar.set(str)
        elif displaySel == DisplayType.MESSAGE_DISPLAY:
            self.__mStrVar.set(str)
    def clear_all_displays(self):
        for d in range(len(DisplayType)-1):
            self.write_display(d, ' ')
    def launch(self):
        self.__root.mainloop() # todo where do I call this and can I call it more than once???
from __future__ import division
from statistics import stdev
import csv
import time
import threading
import serial
import exceptions
import ttk
import Tkinter as Tk
from Tkinter import *
from numpy import arange, sin, pi
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from ScrolledText import ScrolledText
from multiprocessing import Process
from datetime import datetime
import socket
import tkFileDialog
import os
import pandas as pd
import numpy as np
import random
import re
import subprocess

#variable to keep track of column index (intialized to 1 (0 because our get_col_row function takes col-1))
storeVal = 1
i = 0
printFlag = 0
graphFlag = 0
stopFlag = 0


fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

# row indexes of values in log file
numCols = 0
Cnt1Index = 0
Cnt2Index = 0
Conc1Index = 0
Conc2Index = 0
accXIndex = 0
accYIndex = 0
accZIndex = 0
diffPIndex = 0
flowInsideIndex = 0
flowOutsideIndex = 0
serial_data = ''
filter_data = ''
update_period = 5 # period for recieving data
serial_object = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gui = Tk()
gui.title("WRPAS Interface")


# reads output log file in csv format and grabs col, row data
class GrabData():

    # prompts for log file and reads file as csv format & stores row indexes of values
    def __init__(self, f):

        global numCols
        global Cnt1Index
        global Cnt2Index
        global Conc1Index
        global Conc2Index
        global accXIndex
        global accYIndex
        global accZIndex
        global diffPIndex
        global flowInsideIndex
        global flowOutsideIndex
        global MESSAGE
        """
    	filename = tkFileDialog.askopenfilename()
    	pathlabel.config(text=filename)
        """
        
        if MESSAGE == 'DOMDUMP' + '\r':
            with open(f, "r") as f_input:
                csv_input = csv.reader(f_input)
                csv_input.next()
                csv_input.next()
                numCols = len(next(f_input))
                print numCols
                header = csv_input.next()
                #Cnt1Index = header.index("Cnt1:") + 2
                #Cnt2Index = header.index("Cnt2:") + 2
                Conc1Index = header.index("Conc1:") + 2
                Conc2Index = header.index("Conc2:") + 2
                accXIndex = header.index("X:") + 2
                accYIndex = header.index("Y:") + 2
                accZIndex = header.index("Z:") + 2
                diffPIndex = header.index("mt202:") + 2

            #flowInsideIndex = header.index("mt200:") + 2
            #flowOutsideIndex = header.index("mt201:") + 2
                self.details = list(csv_input)
        
        elif MESSAGE == 'CCT 1' + '\r':
            with open(f, "r") as f_input:
                csv_input = csv.reader(f_input)
                #numCols = len(f_input)
                #print numCols
                header = csv_input.next()
                Conc1Index = header.index("Conc1:") + 1
                Conc2Index = header.index("Conc2:") + 1

                self.details = list(csv_input)
        
        elif MESSAGE == 'CAT 1' + '\r':
            with open(f, "r") as f_input:
                csv_input = csv.reader(f_input)
                numCols = len(next(f_input))
                print numCols
                header = csv_input.next()
                accXIndex = header.index("X:") + 2
                accYIndex = header.index("Y:") + 2
                accZIndex = header.index("Z:") + 2
                self.details = list(csv_input)

        else:
            printFlag = 1
            print("no data being displayed")
        

    # references col and row in csv file
    def get_col_row(self, col, row):
        if printFlag == 1:
            return
        else:
            return self.details[row-1][col-1]


"""
class Application(Frame):

    def __init__(self, master):
        Frame.__init__(self,master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self._button = Button(self, text = "TeraTerm Output", command = self._openFile)
        self._button.grid()
"""
def _openFile():
    os.startfile('C:\\Program Files (x86)\\teraterm\\ttermpro.exe') #open up modified TeraTerm

       
# reads what writeTime user chooses and updates when user changes time
def onselect(evt):

	w = evt.widget
	index = int(w.curselection()[0])
	value = w.get(index)
	print 'You selected item %d: "%s"' % (index, value)
	global storeVal
	storeVal = index



def startTransmission():

    global stopFlag
    stopFlag = 0

    TCP_IP = ipentry.get()
    
    if TCP_IP == '':
        udpData("Error: Specify TCP IP")
    else:
        TCP_IP = ipentry.get()
        TCP_PORT = 3602
    

    logData = []
    begin = time.time()
    timeout = 2
    breakInt = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    csvout = logFile.get()

    if csvout == '':
        udpData("Error: Specify Log File Name")
    else:
        csvout = logFile.get()


    path = 'C:/Users/aeros/Desktop/WRPAS-Logs/'

    pathWrite = os.path.join(path, csvout)
    f = open(pathWrite, "a")

    try:
        s.connect((TCP_IP, TCP_PORT))
        udpData("Connected at")
        udpData(TCP_IP)
        udpData("Recieving Data ...")
    except socket.error, e:
        udpData("Failed to connect")
    
    
    while(1):
        if breakInt == 10:
            break 
        if stopFlag == 1:
            udpData("Disconnected")
            break;
        if logData and time.time()-begin > timeout:
            break
        elif time.time()-begin > timeout*2:
            break
        try:
            logData = s.recv(4096)
            f.write(logData)
            udpData(logData)
            if logData:
                begin=time.time()
                loop = loop + 1
            else:
                breakInt = breakInt + 1
                time.sleep(0.1)
        except:
            pass

    

    s.close()
        

def connStatus():

    stopFlag = 0
    print stopFlag

    TCP_IP = ipentry.get()
    TCP_PORT = 3602

    logData = []
    begin = time.time()
    timeout = 2

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((TCP_IP, TCP_PORT))
        udpData("Connected at")
        udpData(TCP_IP)
    except socket.error, e:
        udpData("Failed to connect")
    

    s.sendall('AT+S.STS' + '\r')
    #s.setblocking(0)
    logData = s.recv(1024)
    udpData(logData)

    
    s.close()

def setWiFi():

    stopFlag = 0
    print stopFlag

    TCP_IP = ipentry.get()
    TCP_PORT = 3602

    logData = []
    begin = time.time()
    timeout = 2


    ssidString = ssid.get()
    passwordString = password.get()

    if ssid.get() == '':
        udpData("Error : Specify WiFi SSID")
    else:
        ssidString = ssid.get()

    if passwordString == '':
        udpData("Error : Specify WiFi Password")
    else:
        passwordString = password.get()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((TCP_IP, TCP_PORT))
        udpData("Connected at")
        udpData(TCP_IP)
    except socket.error, e:
        udpData("Failed to connect")


    s.send("DOWIFITEST=1")
    

    s.sendall("AT+S.SSIDTXT=")
    s.send(ssidString)
    s.sendall("AT+S.SCFG=wifi_wpa_psk_text,")
    s.send(passwordString)
    s.sendall("AT+S.SCFG=wifi_priv_mode,2")
    s.sendall("AT+S.SCFG=wifi_mode,1")
    s.sendall("AT&W")
    s.sendall("AT+CFUN=1")

    s.setblocking(0)
    logData = s.recv(4096)
    udpData(logData)

    
    s.close()



	

# for sending data over tcp (commands)
def sendTCP():  

  global logData
  global MESSAGE
  loop = 0
  csvout = "outputTest.txt"
  path = 'C:/Users/aeros/Desktop/WRPAS-Logs/'
  timeout = 2
  newData = []
  logData = []
  TCP_IP = ipentry.get() #user entry
  TCP_PORT = 3602 # user entry
  BUFFER_SIZE = 16000
  MESSAGE = commandentry.get() + '\r' #sends command entered by user

  portNum = Label(text = TCP_PORT).place(x = 800, y = 200)

  
  pathWrite = os.path.join(path, csvout)
  f = open(pathWrite, "a")


   
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #s.settimeout(10)

  try:
    s.connect((TCP_IP, TCP_PORT))
    udpData("Connected at")
    udpData(TCP_IP)
  except socket.error, e:
     udpData("Failed to connect")

  s.sendall(MESSAGE)
  #s.shutdown(socket.SHUT_WR)

  s.setblocking(0) # set port to nonblocking
  
  begin=time.time()     
  output = b''

  if loopInt.get() == '':
    loopTime = 2
  else:
    loopTime = int(loopInt.get()) 


  graphFlag = 1

  while(1):
        if loop == loopTime:
            text1.insert(END, "Stopped Recieving Continious Data... Press SEND to continue recieving data \n")
            text1.insert(END, " To Stop Continious Transimisson, SEND *** 0")
            text1.see("end")
            break;
        if logData and time.time()-begin > timeout:
            #print("in if 1")
            break
        elif time.time()-begin > timeout*2:
            #print("in if 2")
            break
        try:
            logData = s.recv(BUFFER_SIZE).strip('\t\r')
            """
            logData = readline(s)
            print(logData)
            value = parse(logData)
            """
            f.write(logData)
            if logData:
                udpData(logData)
                begin=time.time()
                loop = loop + 1
            else:
                time.sleep(0.1)
        except:
            pass
 
        # perform filtering of strings here or within while loop try?
        # x = logData

        #plt.plot(x, color = 'red', marker = 'o', linestyle = 'dashed', linewidth = 2)
        #plt.show()
        
    

  #print("exited while loop")

  #s.settimeout(None)   
 
  s.close()
  graphFlag = 0





  f.close()
  
  
  file = open(pathWrite, 'r')
  f = open('C:/Users/aeros/Desktop/flashDump.csv', 'wb')
  file.next()
  for line in file:
    x = line
    x = (x.replace(",",""))
    x = (x.replace("CCT 1", ""))
    x = (x.replace("CCT 0", ""))
    x = (x.replace("Conc1:", ""))
    x = (x.replace("Conc2:", ""))
    x = (x.replace("\t", ","))
    f.write(x)
  
  
  openData()
  dataCalc()
  file.close()
  f.close()
  output.close()

def readline(s):

    output = b''
    while not output.endswith(b'\n'):
        output += s.recv(1)
        output.strip('\t')
        time.sleep(0.1)
    return output

def MakeGraph(conn):

    win = pg.GraphicsWindow(title = "test")
    win.resize(300,300)

    p1 = win.addPlot(title = "test")

    curve = p1.plot(pen = 'y')
    timer = QtCore.QTimer()
    CurveData = []

    def Update():
        global CurveData
        try:
            ConnData = conn.recv()
            ConnData = [float(i) for i in ConnData]
            CurveData = np.append(CurveData, ConnData)
            curve.setData(CurveData)
        except EOFError:
            timer.stop()
            QtGui.QApplication.quit()

    timer.timeout.connect(Update)
    timer.start(0)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()



def getData(logData):
    return float(logData)


def animate(i):
    xs = []
    ys = []
    with open('C:/Users/aeros/Desktop/flashDump.csv') as graph_data:
        #numEntry = len(next(graph_data))
        for line in graph_data:
            numEntry = len(line)
            if len(line) > 1:
                lines = line.split(" ")
                lines = line.split(',')
                x, y = lines[1], lines[3]
                xs.append(x)
                ys.append(y)
    ax1.clear()
    ax1.plot(xs)
    ax1.plot(ys)
    ax1.set_xlim(0, 100)



def tcpClear():
    text1.delete('1.0', END)

def udpData(logData):
    text1.insert(END, "\n")
    text1.insert(END, logData)
    text1.insert(END, "\n")
    text1.see("end")
    text1.update()

def tcpDisconnect():
    global stopFlag
    stopFlag = 1

def openData():
    """
    calls function to open log file and read
    """
    global data
    data = GrabData('outputTest.txt')
    return data

def openLog():
    os.system(r"notepad.exe " + "C:\\Users\\aeros\\Desktop\\wifisetup.txt")

def clearLog():
    open("C:\\Users\\aeros\\Desktop\\WRPAS-Logs\\outputTest.txt", 'w').close()


def dataCalc():
 
    """
    Function that takes stored serial data and caculates particle concentration, flow,
    performance factor, and accelorometer data
    """
    global MESSAGE
    global writeTime
    global writeTime1
    global writeTime2
    global writeTime3
    global writeTime4
    global Cnt1
    global Cnt2
    global Cocn1
    global Conc2
    global mt200
    global mt201
    global mt202
    global TDcond
    global TDmod
    global Ths 
    global Tpcb
    global Tbatt
    global Pcond
    global Pinit
    global Pmod
    global Ptotal
    global accX
    global avgX
    global accY
    global avgY
    global accZ
    global avgZ
    global data
    global maxG


    div = 5.000 # averaging factor

    Cnt1 = data.get_col_row(Conc1Index, storeVal) #Inside
    Cnt2 = data.get_col_row(Conc2Index, storeVal) #Outside
    
    # acceleration X
    
    accX = data.get_col_row(accXIndex, storeVal)
    avgX = float(data.get_col_row(accXIndex, storeVal)) + float(data.get_col_row(accXIndex, storeVal + 1)) + float(data.get_col_row(accXIndex, storeVal + 2)) + float(data.get_col_row(accXIndex, storeVal + 3)) + float(data.get_col_row(accXIndex, storeVal + 4))
    avgX = float(avgX)/float(div)
    avgX = round(avgX, 3)

    # acceleration Y
    accY = data.get_col_row(accYIndex, storeVal)
    avgY = float(data.get_col_row(accYIndex, storeVal)) + float(data.get_col_row(accYIndex, storeVal + 1)) + float(data.get_col_row(accYIndex, storeVal + 2)) + float(data.get_col_row(accYIndex, storeVal + 3)) + float(data.get_col_row(accYIndex, storeVal + 4))
    avgY = float(avgY)/float(div)
    avgY = round(avgY, 3)

    # acceleration Z
    accZ = data.get_col_row(accZIndex, storeVal)
    avgZ = float(data.get_col_row(accZIndex, storeVal)) + float(data.get_col_row(accZIndex, storeVal + 1)) + float(data.get_col_row(accZIndex, storeVal + 2)) + float(data.get_col_row(accZIndex, storeVal + 3)) + float(data.get_col_row(accZIndex, storeVal + 4))
    avgZ = float(avgZ)/float(div)
    avgZ = round(avgZ, 3)	

    #maxg, loop through row of corresponding acceleration col, and return max
    max_x = max(data.get_col_row(accXIndex, storeVal), data.get_col_row(accXIndex, storeVal + 1), data.get_col_row(accXIndex, storeVal + 2), data.get_col_row(accXIndex, storeVal + 3), data.get_col_row(accXIndex, storeVal + 4)) 
    max_y = max(data.get_col_row(accYIndex, storeVal), data.get_col_row(accYIndex, storeVal + 1), data.get_col_row(accYIndex, storeVal + 2), data.get_col_row(accYIndex, storeVal + 3), data.get_col_row(accYIndex, storeVal + 4))    
    max_z = max(data.get_col_row(accZIndex, storeVal), data.get_col_row(accZIndex, storeVal + 1), data.get_col_row(accZIndex, storeVal + 2), data.get_col_row(accZIndex, storeVal + 3), data.get_col_row(accZIndex, storeVal + 4))
    
    #stdvg (standard variance), use numpy.var and numpy.std to calculate
    stdv_x = np.std([float(data.get_col_row(accXIndex, storeVal)), float(data.get_col_row(accXIndex, storeVal + 1)), float(data.get_col_row(accXIndex, storeVal + 2)), float(data.get_col_row(accXIndex, storeVal + 3)), float(data.get_col_row(accXIndex, storeVal + 4))], ddof = 0)
    stdv_x = round(stdv_x, 2)
    stdv_y = np.std([float(data.get_col_row(accYIndex, storeVal)), float(data.get_col_row(accYIndex, storeVal + 1)), float(data.get_col_row(accYIndex, storeVal + 2)), float(data.get_col_row(accYIndex, storeVal + 3)), float(data.get_col_row(accYIndex, storeVal + 4))], ddof = 1)
    stdv_y = round(stdv_y, 2)
    stdv_z = np.std([float(data.get_col_row(accZIndex, storeVal)), float(data.get_col_row(accZIndex, storeVal + 1)), float(data.get_col_row(accZIndex, storeVal + 2)), float(data.get_col_row(accZIndex, storeVal + 3)), float(data.get_col_row(accZIndex, storeVal + 4))], ddof = 1)
    stdv_z = round(stdv_z, 2)

    #C_in for steps, need output of fit test data

    #PF & avgPF   
    
    """
    """
    if float(Cnt1) <= 0:
        print "Outside concentration too low, choose different write time & Update Data"
    else:
        currPF = float(Cnt2)/float(Cnt1)
        currPF = round(currPF, 1)
    """
    """

    # Concetration avgs
    avgConc1 = float(data.get_col_row(Conc1Index, storeVal)) + float(data.get_col_row(Conc1Index, storeVal + 1)) + float(data.get_col_row(Conc1Index, storeVal + 2)) + float(data.get_col_row(Conc1Index, storeVal + 3)) + float(data.get_col_row(Conc1Index, storeVal + 4))
    avgConc2 = float(data.get_col_row(Conc2Index, storeVal)) + float(data.get_col_row(Conc2Index, storeVal + 1)) + float(data.get_col_row(Conc2Index, storeVal + 2)) + float(data.get_col_row(Conc2Index, storeVal + 3)) + float(data.get_col_row(Conc2Index, storeVal + 4))   
   
    # average protection factor
    """
    """
    if float(avgConc1) <= 0:
        print "Outside concentration too low, choose different write time & Update Data"
    else:    
        avgPF = float(avgConc2)/float(avgConc1)
        avgPF = round(avgPF, 1) 
    """
    """ 

    #dP
    diffP = float(data.get_col_row(diffPIndex, storeVal))  


    # flow rates
    #flowInside = float(data.get_col_row(flowInsideIndex, storeVal))
    #flowOutside = float(data.get_col_row(flowOutsideIndex, storeVal))
    """

    count1 = Label(text = Cnt1).place(x = 1150, y = 150)
    
    count2 = Label(text = Cnt2)
    count2.place(x = 1200, y = 100)

    """
    acceX = Label(text = accX)
    acceX.place(x = 1100, y = 850)

    avgaccX = Label(text = avgX)
    avgaccX.place(x = 1150, y = 850)

    acceY = Label(text = accY)
    acceY.place(x = 1100, y = 900)

    acceZ = Label(text = accZ)
    acceZ.place(x = 1050, y = 950)

    avgaccY = Label(text = avgY)
    avgaccY.place(x = 1150, y = 900)

    avgaccZ = Label(text = avgZ)
    avgaccZ.place(x = 1100, y = 950)

    maxgX = Label(text = max_x)
    maxgX.place(x = 1200, y = 850)

    maxgY = Label(text = max_y)
    maxgY.place(x = 1200, y = 900)

    maxgZ = Label(text = max_z)
    maxgZ.place(x = 1150, y = 950)

    #currentPF = Label(text = currPF)
    #currentPF.place(x = 540, y = 320)

    stdX = Label(text = stdv_x)
    stdX.place(x = 1250, y = 850)
    
    stdY = Label(text = stdv_y)
    stdY.place(x = 1250, y = 900)

    stdZ = Label(text = stdv_z)
    stdZ.place(x = 1200, y = 950)

    #averagePF = Label(text = avgPF).place(x = 540, y = 340)

    dPCalc = Label(text = diffP).place(x = 1500, y = 150)

    #flowin = Label(text = flowInside).place(x = 680, y = 140)
    #flowout = Label(text = flowOutside).place(x = 680, y = 120)
    
    counter = 0

    while counter < 4: 
        mylistbox.insert(END, data.get_col_row(1, counter))
        counter = counter + 1

    #mylistbox.place(x = 20, y = 250)
    

    
    gui.after(1000, dataCalc) # updates gui every second


# create new frame for graphs in tkinter (not done)
"""
class newPage:

    def __init__(self, window):

        self.window = window
        self.box = Entry(window)

        self.button = Button(window, text = "check", command = self.plot)
        self.box.pack()
        self.button.pack()

    def plot (self):
       
        df = pd.read_csv(data)
        x = df["X Data"]
        y1 = df["Y1 Data"]
        y_pos = np.arrange(len(x))
    

        x=np.array ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        v= np.array ([16,16.31925,17.6394,16.003,17.2861,17.3131,19.1259,18.9694,22.0003,22.81226])
        p= np.array ([16.23697,     17.31653,     17.22094,     17.68631,     17.73641 ,    18.6368,
            19.32125,     19.31756 ,    21.20247  ,   22.41444   ,  22.11718  ,   22.12453])



        fig = Figure(figsize=(6,6))
        a = fig.add_subplot(111)
        a.scatter(v,x,color='red')
        a.plot(p, range(2+max(x)), color='blue')
        a.invert_yaxis()

        a.set_title("Concetration vs Time", fontsize=16)
        a.set_ylabel("Y", fontsize=14)
        a.set_xlabel("X", fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().pack()
        canvas.draw()

window = Tk()
start = newPage (window)
window.mainloop()
"""


# example graphing
class ServoDrive(object):
    # simulate values
    
    def getVelocity(self):
        return random.randint(0, 50)

    def getTorque(self): 
        return random.randint(50, 100)

class Example(Frame):
    def __init__(self, *args, **kwargs):
        
        Frame.__init__(self, *args, **kwargs)
        self.servo = ServoDrive()
        self.canvas = Canvas(self, background="black")
        self.canvas.pack(side="top", fill="both", expand=True)
        
        # create lines for velocity and torque
        self.velocity_line = self.canvas.create_line(0,0,0,0, fill="red")
        self.torque_line = self.canvas.create_line(0,0,0,0, fill="blue")

        # start the update process
        self.update_plot()

    def update_plot(self):
        v = self.servo.getVelocity()
        t = self.servo.getTorque()
        self.add_point(self.velocity_line, v)
        self.add_point(self.torque_line, t)
        self.canvas.xview_moveto(1.0)
        self.after(100, self.update_plot)

    def add_point(self, line, y):
        coords = self.canvas.coords(line)
        x = coords[-2] + 8
        coords.append(x)
        coords.append(y)
        coords = coords[-500:] # keep # of points to a manageable size
        self.canvas.coords(line, *coords)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))



if __name__ == "__main__":

    
    """
    The main loop consists of all the GUI objects and its placement.
    The Main loop handles all the widget placements.
    """

    # Threads to run functions in
    thread = threading.Thread(target=sendTCP)
    thread.daemon = True
    thread.start()

    t2 = threading.Thread(target=udpData)
    t2.daemon = True
    t2.start()

    t3 = threading.Thread(target=startTransmission)
    t3.daemon = True
    t3.start()

    







    #frames
    frame1 = Frame(height = 500, width = 2000, bd = 3, relief = 'groove').place(x = 7, y = 20)


    #text1 = Text(width = 60, height = 5)
    text1 = ScrolledText(width = 180, height = 23)
    text1.config(font=("Courier", 10))
    text1.place(x = 5, y = 520)

    dataOut = Label(text = "Data Output", font = 48).place(x = 800, y = 480)

    wrpasTitle = Label(text = "WRPAS WIFI INTERFACE", font = 80, fg = "black").place(x = 680, y = 30)



    #BUTTONS
    getData = Button(text = "COLLECT DATA", command = startTransmission, font = 128, fg = "green")
    getData.place(x = 700, y = 100)

    teraTerm = Button(text = "CONNECT IN TERATERM", command = _openFile, font = 128)
    teraTerm.place(x = 700, y = 200)

    closeConn = Button(text = "DISCONNECT", command = tcpDisconnect, font = 128, fg = "red")
    closeConn.place(x = 700, y = 300)

    clearData = Button(text = "CLEAR DATA OUTPUT", command = tcpClear, font = 128)
    clearData.place(x = 1400, y = 450)

    #connStatus = Button(text = "Check Connection Status", command = connStatus, font = 128)
    #connStatus.place(x = 50, y = 400)

    setWiFiParams = Button(text = "Set WiFi Params w/TeraTerm", command = _openFile, font = 128)
    setWiFiParams.place(x = 50, y = 250)

    editWiFi = Button(text = "Edit WiFi Parameters", command  = openLog, font = 128)
    editWiFi.place(x = 50, y = 100)

    #setWifiButton = Button(text = "Set WiFi Parameters", command = setWiFi, font = 128)
    #setWifiButton.place(x = 50, y = 200)



    wifiConn = Label(text = "WiFi Connection Setup", font = 128)
    wifiConn.place(x = 50, y = 30)

    """
    ssidLabel = Label(text = "WiFi SSID")
    ssidLabel.place(x = 30, y = 100)

    passLabel = Label(text = "WiFi Password")
    passLabel.place(x = 30, y = 150)
    """

    step1 = Label(text = "1. Set Connection Parameters through WiFi Params file").place(x = 1100, y = 50)
    step11 = Label(text = "2. Click Set WiFi Params and through the Serial Port enter DOWIFITEST=1").place(x = 1100, y = 100)
    step23 = Label(text = "3. Send WiFi Params File through TeraTerm and a connection should establish").place(x = 1100, y = 150)
    step2 = Label(text = "4. Enable WiFi on WRPAS under WiFi Menu").place(x = 1100, y = 200)
    step3 = Label(text = "5. Enable Continious Data on WRPAS under WiFi Menu & Enable Socket Host").place(x = 1100, y = 250)
    step4 = Label(text = "6. Get TCP IP from output of connection status on TeraTerm").place(x = 1100, y = 300)
    step5 = Label(text = "7. Begin Collecting Data").place(x = 1100, y = 350)

    """
    conn1 = Label(text = "AT+S.SSIDTXT=[SSID]").place(x = 50, y = 150)
    conn2 = Label(text = "AT+S.SCFG=wifi_wpa_psk_text,[password]").place(x = 50, y = 180)
    conn3 = Label(text = "AT+S.SCFG=wifi_priv_mode,2").place(x = 50, y = 210)
    conn4 = Label(text = "AT+S.SCFG=wifi_mode,1").place(x = 50, y = 240)
    conn5 = Label(text = "AT&W").place(x = 50, y = 270)
    conn6 = Label(text = "AT+CFUN=1").place(x = 50, y = 300)


    conn8 = Label(text = "Connect to WRPAS through Serial Port and type DOWIFITEST=1").place(x = 50, y = 400)
    conn7 = Label(text = "Send above commands with respective SSID and Password through Serial Port to Set WiFi").place(x = 50, y = 430)
    """






    #ENTRIES
    logFile = Entry(width = 20)
    logFile.place(x = 850, y = 350)

    ipentry = Entry(width = 20)
    ipentry.place(x = 850, y = 450)

    logFileName = Label(text = "Log File Name", font = 64).place(x = 700, y = 350)
    logExample = Label(text = "Example (WiFiData.txt)", font = 64).place(x = 700, y = 390)
    ipName = Label(text = "TCP IP", font = 64).place(x = 700, y = 450)

    """
    ssid = Entry(width = 25)
    ssid.place(x = 140, y = 100)

    password = Entry(width = 25)
    password.place(x = 140, y = 150)
    """
    



    root = Tk()
    #mainloop
    gui.geometry('500x500')

    #ani = animation.FuncAnimation(fig, animate, interval = 1000)
    #plt.show()

    #app = Application(root).pack(side="top", fill="both", expand=True)

gui.mainloop()

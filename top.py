# -*- coding: utf-8 -*-
# Created by: PyQt5 UI code generator 5.5.1

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from  graph import Graph
import serial_util as su

# For embedding matplotlib(used for plotting NetworkX graph) navigation toolbar on our app window
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("ESP8266 Mesh Network Visualizer")
        self.mainX = 600
        self.mainY = 600
        MainWindow.resize(self.mainX, self.mainY)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.graph = Graph()  # yoppy

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.graph.canvas, self)

        # init and open serial port
        # SET COMxx to the corresponding serial port number used by the ESP
        self.comPortNum = 'COM3'
        self.ser_ref = su.init_serial(comPort=self.comPortNum)

        # create a thread to read from serial:
        # - for checking mesh topology changes. whenever there is a change, the mesh is redrawn
        # - for receiving replies from other nodes
        ser_read_thread = SerialThread(self.ser_ref)
        ser_read_thread.updateNodeSig.connect(self.graph.updateNodes)
        ser_read_thread.updateNodeData.connect(self.graph.updateNodeData)
        ser_read_thread.start()


        # define label for showing serial port settings
        self.serialSettingLabel = QLabel(self.centralwidget)
        serialSetting = 'Port: ' + str(self.ser_ref.port) + '. Baud rate: ' + str(self.ser_ref.baudrate)
        self.serialSettingLabel.setText(serialSetting)

        MainWindow.setCentralWidget(self.centralwidget)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.graph.canvas)
        layout.addWidget(self.serialSettingLabel)
        self.centralwidget.setLayout(layout)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    


class SerialThread(QtCore.QThread):

    updateNodeSig = QtCore.pyqtSignal(object)
    myFreeMemSig = QtCore.pyqtSignal(object)
    updateNodeData = QtCore.pyqtSignal(object)

    def __init__(self, ser_ref):
        QtCore.QThread.__init__(self)
        self.serialPort = ser_ref
        self.oldJsonString = None

    def run(self):

        while True:

            # Wait for new string from serial port
            while True:
                msgType, jsonString = su.read_json_string(self.serialPort)  # read a '\n' terminated line
                if jsonString != None:
                    break

            # Please uncomment to deliberately redraw mesh every time serial is received
            # Otherwise, the figure is only redrawn when there is a change in the mesh topology
            #self.oldJsonString = None

            if (msgType == 'MeshTopology'):
                # Check if the mesh topology has changed
                if self.oldJsonString != jsonString:
                    self.oldJsonString = jsonString
                    self.updateNodeSig.emit(jsonString)
                    self.sleep(1)

            if (msgType == 'SendData'):
                self.updateNodeData.emit(jsonString)
            






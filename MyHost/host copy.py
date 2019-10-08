# original one 

import sys 
from PyQt5 import QtCore , QtGui , QtWidgets 
from PyQt5.QtWidgets import QDialog 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QApplication

import cv2 
import socket 
import json 
from color_feature import color_block_finder, findMaxRect , draw_color_block_rect


class myHost(QDialog):
    def __init__(self,*args ):
        #init 
        super(myHost,self).__init__(*args)
        loadUi('./host.ui',self)
        
        #camera 
        self.cam = cv2.VideoCapture(1)
        self.startVideo = False 
        self.timerCamera = QtCore.QTimer()
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.videoWritter = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
        
        #color detect 
        self.hueL = 0 
        self.hueH = 0 
        self.satL = 0 
        self.satH = 0 
        self.valL = 0 
        self.valH = 0 
        
        # car connect 
        self.carAddress = "127.0.0.1"
        self.carClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.carCoon = False 
        
        #connect slot 
        self.videoStartButton.clicked.connect(self.slotVideoStart)
        self.videoEndButton.clicked.connect(self.slotVideoEnd)
        self.exitButton.clicked.connect(self.slotExit)
        
        self.timerCamera.timeout.connect(self.slotUpdateFrame)
        
        self.hueLSpinBox.valueChanged.connect(self.slotUpdateBound)
        self.hueHSpinBox.valueChanged.connect(self.slotUpdateBound)
        self.satLSpinBox.valueChanged.connect(self.slotUpdateBound)
        self.satHSpinBox.valueChanged.connect(self.slotUpdateBound)
        self.valLSpinBox.valueChanged.connect(self.slotUpdateBound)
        self.valHSpinBox.valueChanged.connect(self.slotUpdateBound)
        
        self.connectButton.clicked.connect(self.slotConnect)
        
        #check camera 
        if(self.cam.isOpened()):
            msg = QtWidgets.QMessageBox.information(self,u"Info",u"Camera is opened",
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            
            if(self.timerCamera.isActive() == False):
                self.timerCamera.start(30)
        else:
            msg = QtWidgets.QMessageBox.information(self,u"Error",u"Camera not opened. Please check your camera",
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            self.slotExit()
     
    # basic function 
    def packMsg(self,x,y):
        json = {}
        json['x'] = x 
        json['y'] = y 
        return json 
     
    # slot function    
    def slotVideoStart(self):
        if self.cam.isOpened() :
            self.startVideo = True 
        
    def slotVideoEnd(self):
        self.startVideo = False 
        
    def slotUpdateBound(self):
        self.hueL = self.hueLSpinBox.value()
        self.hueH = self.hueHSpinBox.value()
        self.satL = self.satLSpinBox.value()
        self.satH = self.satHSpinBox.value()
        self.valL = self.valLSpinBox.value()
        self.valH = self.valHSpinBox.value()
        
    def slotConnect(self):
        # clear 
        if self.carCoon == True:
            self.carClient.close()
            self.carCoon = False    
    
        # get new car ip 
        self.carAddress = self.ipCarLineEdit.text()
        
        # connect, begin transfer 
        self.carClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.carClient.connect((self.carAddress,9010))      # here is the car port, check if it work 
        
        #confirm connection 
        back_msg = self.carClient.recv(1024)

        if len(back_msg) !=0:
            msg = QtWidgets.QMessageBox.information(self,u"Info",u"connect to %s port %s done."%(self.carAddress,9010),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)

            print("recv from server: ",back_msg)
            
            self.carCoon = True
            
        else:
            print("connection failed!")
            
            msg = QtWidgets.QMessageBox.information(self,u"Error",u"connect to %s port %s fail."%(self.carAddress,9010),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
        
        
    def slotExit(self):
        self.timerCamera.stop()
        self.videoWritter.release()
        
        if self.cam.isOpened():
            self.cam.release()
            
        if self.carCoon == True:
            self.carClient.close()
            self.carCoon = False
        
        self.close()
        
    def slotUpdateFrame(self):
        ret , frame = self.cam.read()
        if ret == True:
            #color find 
            lowerb = (self.hueL,self.satL,self.valL)
            upperb = (self.hueH,self.satH,self.valH)
            rects = color_block_finder(frame,lowerb,upperb)
            
            #find possible rect 
            rect = findMaxRect(rects)
            
            #draw 
            frame = draw_color_block_rect(frame,[rect])
            
            #save video 
            if self.startVideo == True:
                self.videoWritter.write(frame)  
                
            #show 
            show = cv2.resize(frame,(800,800))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.videoLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))

            #change coordinate 
            if(len(rect)!=0):
                self.xLabel.setText(str(rect[0]+0.5*rect[2]))
                self.yLabel.setText(str(rect[1]+0.5*rect[3]))
                
                #broadcast coordinate 
                if self.carCoon == True: 
                    msg = json.dumps(self.packMsg(rect[0] + 0.5 * rect[2], rect[1] + 0.5 * rect[3]))
                    msg += "\n"
                    self.carClient.sendall(msg.encode())
                    print("send msg to car: " + msg)
    
    def closeEvent(self,event):
        #close camera 
        if self.cam.isOpened():
            self.cam.release()
            self.videoWritter.release()
            
        #close timer 
        if self.timerCamera.isActive():
            self.timerCamera.stop()
            
        #close client 
        if self.carCoon == True: 
            self.carCoon = False 
            self.carClient.close()
            
        event.accept()
        
        
if __name__ == "__main__":
    #init 
    app = QApplication(sys.argv)
    
    #config 
    host = myHost()
    if host.cam.isOpened():
        host.show()
        
        #begin 
        sys.exit(app.exec_())
    
    else:
        print("cannot open camera. Please check camera connection")
        

    
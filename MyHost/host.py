import sys 
from PyQt5 import QtCore , QtGui , QtWidgets 
from PyQt5.QtWidgets import QDialog 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QApplication

import errno 
import cv2 
import math 
import numpy as np 
import socket 
import json 
import time 
import autoRect
from color_feature import color_block_finder, findMaxRect , draw_color_block_rect
from ETManager import ETManager 

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
        self.videoWritter = cv2.VideoWriter('camera.avi',fourcc, 20.0, (800,800))
        
        #eye camera 
        self.eyeVideoWritter = cv2.VideoWriter('eye.avi',fourcc, 20.0, (800,800))
        self.eyeRectVideoWritter = cv2.VideoWriter('eye_rect.avi',fourcc, 20.0 ,(800,800))
        self.pauseFlag = False 
        self.eyeFrame = np.zeros((640,480,3), np.uint8)   
        self.eyeX = 0 
        self.eyeY = 0 
        
        
        # front color detect : blue 
        self.hueL = self.hueLSpinBox.value()
        self.hueH = self.hueHSpinBox.value()
        self.satL = self.satLSpinBox.value()
        self.satH = self.satHSpinBox.value()
        self.valL = self.valLSpinBox.value()
        self.valH = self.valHSpinBox.value()
        
        # back color detect  : red 
        self.hueL2 = self.hueL2SpinBox.value()
        self.hueH2 = self.hueH2SpinBox.value()
        self.satL2 = self.satL2SpinBox.value()
        self.satH2 = self.satH2SpinBox.value()
        self.valL2 = self.valL2SpinBox.value()
        self.valH2 = self.valH2SpinBox.value()
        
        # car connect 
        self.carAddress = self.ipCarLineEdit.text()
        self.carClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.carCoon = False
        
        # eye connect 
        self.etCoon = False 
        self.etAddress = self.ipEyeLineEdit.text()
        self.etManager = ETManager(appHost=self.etAddress) 
        
        # get host ip 
        hostname = socket.gethostname()
        self.ipAddress = socket.gethostbyname(hostname)
        self.ipMeLabel.setText(self.ipAddress)
        
        # rectify cam pic 
        self.rectify = False 
        self.box = []
        
        # rectify eye pic 
        self.eyeRectify = False 
        self.eyeOriginal = True 
        self.eyeBox = [] 
        
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
        
        self.hueL2SpinBox.valueChanged.connect(self.slotUpdateBound)
        self.hueH2SpinBox.valueChanged.connect(self.slotUpdateBound)
        self.satL2SpinBox.valueChanged.connect(self.slotUpdateBound)
        self.satH2SpinBox.valueChanged.connect(self.slotUpdateBound)
        self.valL2SpinBox.valueChanged.connect(self.slotUpdateBound)
        self.valH2SpinBox.valueChanged.connect(self.slotUpdateBound)
        
        self.connectButton.clicked.connect(self.slotConnect)
        self.pauseButton.clicked.connect(self.slotPause)
        
        self.resetButton.clicked.connect(self.slotReset)
        self.eyeResetButton.clicked.connect(self.slotEyeReset)
        self.eyeOriButton.clicked.connect(self.slotEyeOriginal)
        
        
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
    def packMsg(self,x,y,angle,desX,desY):
        json = {}
        json['x'] = x 
        json['y'] = y 
        json['angle'] = angle 
        json['desX'] = desX 
        json['desY'] = desY 
        return json 
     
    # broadcast coordinate 
    def sendToCar(self,coreX,coreY,angle,desX,desY): 
        if self.carCoon == True: 
            msg = json.dumps(self.packMsg(coreX, coreY, angle,desX,desY))
            msg += "\n"
            self.carClient.sendall(msg.encode())
            print("send msg to car: " + msg)
     
    # slot function   
    def slotPause(self): 
        self.pauseFlag = not self.pauseFlag 
            
        print("------------pause----------------") 
     
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
        
        self.hueL2 = self.hueL2SpinBox.value()
        self.hueH2 = self.hueH2SpinBox.value()
        self.satL2 = self.satL2SpinBox.value()
        self.satH2 = self.satH2SpinBox.value()
        self.valL2 = self.valL2SpinBox.value()
        self.valH2 = self.valH2SpinBox.value()
                
    def slotConnect(self):
        # clear 
        if self.carCoon == True:
            self.carClient.close()
            self.carCoon = False    
    
        if self.etCoon == True:
            self.etManager.close()
            self.etCoon = False   
        
        # get new car ip 
        self.carAddress = self.ipCarLineEdit.text()
        self.ipCarLabel.setText(self.carAddress)
        
        # get new et manager ip 
        self.etAddress = self.ipEyeLineEdit.text()
        self.ipEyeLabel.setText(self.etAddress)
        
        # car connect, begin transfer 
        self.carClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        try: 
            self.carClient.connect((self.carAddress,9010))      # here is the car port, check if it work 
        except socket.error as e : 
            err = e.args[0] 
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                time.sleep(1)
            print("car conn got socket exception: " + str(e))
            
        except BaseException as b: 
            print("other exception: " + str(b))
        
        
        #confirm connection 
        print("confirm conn")
        time.sleep(1)
        try: 
            back_msg = self.carClient.recv(1024)
        except BaseException as b: 
            print("confirm exception: " + str(b))
            back_msg = ""
            
        if len(back_msg) !=0:
            msg = QtWidgets.QMessageBox.information(self,u"Info",u"connect to %s port %s done."%(self.carAddress,9010),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            print("recv from server: ",back_msg)
            
            self.carCoon = True
            
        else:
            print("connection failed!")
            
            msg = QtWidgets.QMessageBox.information(self,u"Error",u"connect to %s port %s fail."%(self.carAddress,9010),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
        
        # eye connect, begin transfer
        self.etManager = ETManager(appHost=self.etAddress)
        self.etManager.start() 
        
        # confirm connection 
        if self.etManager.conn == True and self.etManager.imgConn == True: 
            msg = QtWidgets.QMessageBox.information(self,u"Info",u"connect to %s port %s and %s done."%(self.carAddress,9011,9013),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)            
            self.etCoon = True 

        elif self.etManager.imgConn == False:    
            msg = QtWidgets.QMessageBox.information(self,u"Error",u"connect to %s port %s fail."%(self.carAddress,9013),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            msg = QtWidgets.QMessageBox.information(self,u"Error",u"connect to %s port %s fail."%(self.carAddress,9011),
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
        
        self.startVideo = True
        
    def slotExit(self):
        self.timerCamera.stop()
        self.videoWritter.release()
        self.eyeVideoWritter.release()
        self.eyeRectVideoWritter.release()
        
        
        if self.cam.isOpened():
            self.cam.release()
            
        if self.carCoon == True:
            self.carClient.close()
            self.carCoon = False
        
        if self.etCoon == True:
            self.etManager.close()
            self.etCoon = False 
        
        self.close()
        
    def slotUpdateFrame(self):
        # camera frame 
        ret , frame = self.cam.read()
        
        if ret == True:
            # first rectfy img 
            if self.rectify == False: 
                frame , grayImg , RedThre , closed , opened = autoRect.ImgOutline(frame)
                
                box , drawImg = autoRect.findContours(frame,opened)
                if len(box) == 0:
                    print("no box find")
                else:
                    self.box = box 
                    self.rectify = True 
                    
                    self.leftUpLabel.setText(str(box[0]))
                    self.rightUpLabel.setText(str(box[1]))
                    self.leftDownLabel.setText(str(box[2]))
                    self.rightDownLabel.setText(str(box[3]))

            # get rectified frame 
            if len(self.box) !=0: 
                frame = autoRect.perspectiveTrans(self.box,frame)
                frame = cv2.resize(frame, (800,800))
            
            # front color find : blue  
            lowerb = (self.hueL,self.satL,self.valL)
            upperb = (self.hueH,self.satH,self.valH)
            rects = color_block_finder(frame,lowerb,upperb)
            
            #find possible rect 
            rect = findMaxRect(rects)
            
            #draw 
            draw_frame = draw_color_block_rect(frame,[rect],color=(255,0,0))
            
            # back color find 
            lowerb = (self.hueL2,self.satL2,self.valL2)
            upperb = (self.hueH2,self.satH2,self.valH2)
            rectsBack = color_block_finder(frame,lowerb,upperb)
            
            rectBack = findMaxRect(rectsBack)
            
            # second draw 
            frame = draw_color_block_rect(draw_frame,[rectBack])
         
            #save video 
            if self.startVideo == True:
                self.videoWritter.write(frame)  
                
            #show 
            show = cv2.resize(frame,(800,800))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.videoLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))

            #cal coordinate  
            if len(rect)!=0 and len(rectBack) != 0 :
                frontX = rect[0]+0.5*rect[2]
                frontY = rect[1]+0.5*rect[3]
                
                backX = rectBack[0]+0.5*rectBack[2]
                backY = rectBack[1]+0.5*rectBack[3]
                
                coreX = ( frontX + backX )/2
                coreY = ( frontY + backY )/2
                
                angle = math.atan2((frontY - backY), (frontX - backX))
                
                angle = float(("%.2f"%angle))
            else:
                coreX = 0 
                coreY = 0 
                angle = float(("%.2f"%(0)))
                
            #set text     
            self.xLabel.setText(str(coreX))
            self.yLabel.setText(str(coreY))
            self.angleLabel.setText(str(angle))
            
        else: 
            coreX = 0 
            coreY = 0 
            angle = 0 
        
        #eye frame
           
        write_originalImage = self.etManager.getImage() 
        write_originalImage = cv2.resize(write_originalImage,(800,800))
        self.eyeRectVideoWritter.write(write_originalImage)  
        
        if self.pauseFlag == False: 
            eyeFrame = write_originalImage
            self.eyeFrame = eyeFrame 
        else: 
            eyeFrame = self.eyeFrame 
        
        if self.etCoon == True : 
            # first rectfy img 
            if self.eyeRectify == False: 
                #eyeFrame = self.etManager.getImage()
                eyeFrame , grayImg , RedThre , closed , opened = autoRect.ImgOutline(eyeFrame)
                
                box , drawImg = autoRect.findContours(eyeFrame,opened)
                
                if len(box) == 0:
                    print("no box find")
                else:
                    self.eyeBox = box 
                    self.eyeRectify = True 
                    
                    self.eyeLeftUpLabel.setText(str(box[0]))
                    self.eyeRightUpLabel.setText(str(box[1]))
                    self.eyeLeftDownLabel.setText(str(box[2]))
                    self.eyeRightDownLabel.setText(str(box[3]))
            
                   
            # then get rectified frame 
            if len(self.eyeBox) != 0: 
                new_eyeFrame = autoRect.perspectiveTrans(self.eyeBox,eyeFrame)
            
            new_eyeFrame = cv2.resize(new_eyeFrame, (800,800))
                
            #show 
            if self.eyeOriginal == False : 
                show = cv2.resize(new_eyeFrame,(800,800))
            else: 
                show = cv2.resize(eyeFrame,(800,800))
                
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.eyeVideoLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))

            #save video 
            if self.startVideo == True:
                self.eyeVideoWritter.write(new_eyeFrame)      
    
            # begin cal 
            if len(self.eyeBox) != 0 :
                eyeX, eyeY = self.etManager.eyePos()
                
                oriCoor = np.array([[eyeX],
                                    [eyeY],
                                    [1]])
                
                T = autoRect.getTransMat(self.eyeBox,self.etManager.img)
                
                # get new coor 
                newCoor = np.dot(T,oriCoor)
                
                desX_ = newCoor[0][0]
                desY_ = newCoor[1][0]
                desZ_ = newCoor[2][0]
                
                #desX = int(desX_/desZ_)
                #desY = int(desY_/desZ_)
                if self.pauseFlag == False: 
                    desX = int(eyeX*800/640) 
                    desY = int(eyeY*800/480)
                    
                    self.eyeX = desX 
                    self.eyeY = desY  
                else: 
                    desX = self.eyeX 
                    desY = self.eyeY 
                    
                # little revise 
                if desX < 0: 
                    desX = 0 
                if desX > 800: 
                    desX = 800 
                if desY < 0 : 
                    desY = 0 
                if desY > 800: 
                    desY = 800 
                
            else:
                print("eye pos not rectified")
                desX = 0 
                desY = 0 
                
            # set text 
            self.desXLabel.setText(str(desX))
            self.desYLabel.setText(str(desY))
            
        else: 
            # show black img 
            falseFrame = np.zeros((800,800,3),np.uint8)

            #show 
            show = cv2.cvtColor(falseFrame, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.eyeVideoLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))
            
            # pass wrong corr
            desX, desY = self.etManager.eyePos()
            
            # set text 
            self.desXLabel.setText(str(desX))
            self.desYLabel.setText(str(desY))
            
        #send to car 
        self.sendToCar(coreX,coreY,angle,desX,desY)     
        
    def slotReset(self):
        self.rectify = False 
    
    def slotEyeReset(self):
        self.eyeRectify = False
        self.eyeOriginal = False 
        
    def slotEyeOriginal(self):
        self.eyeOriginal = True 
    
    # event 
    def closeEvent(self,event):
        #close camera 
        if self.cam.isOpened():
            self.cam.release()
        
        self.videoWritter.release()
        #close eye video Writter 
        self.eyeVideoWritter.release()
        self.eyeRectVideoWritter.release()
        
        #close timer 
        if self.timerCamera.isActive():
            self.timerCamera.stop()
            
        #close client 
        if self.carCoon == True: 
            self.carCoon = False 
            self.carClient.close()
            
        #close etManager 
        if self.etCoon == True:
            self.etManager.close()
            self.etCoon = False 
            
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
        

    
import sys 
from PyQt5 import QtCore , QtGui , QtWidgets 
from PyQt5.QtWidgets import QDialog 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QApplication
import cv2 


class tryHost(QDialog):
    def __init__(self, *args):
        #init 
        super(tryHost,self).__init__(*args)
        loadUi('./videoShow.ui',self)
        
        #begin camera 
        self.cam = cv2.VideoCapture(1)
        self.startVideo = False
        self.timerCamera = QtCore.QTimer()
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.videoWritter = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
        
        #connect slot 
        self.videoStartButton.clicked.connect(self.slotVideoStart)
        self.videoEndButton.clicked.connect(self.slotVideoEnd)
        self.exitButton.clicked.connect(self.slotExit)
        
        self.timerCamera.timeout.connect(self.showCamera)
        
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
            
    def slotVideoStart(self):
        if(self.cam.isOpened()):
            self.startVideo = True 
            
    def slotVideoEnd(self):
        self.startVideo = False 
        
    def slotExit(self):
        self.timerCamera.stop()
        self.videoWritter.release()
        self.cam.release()
        
        self.close()
        
    def showCamera(self):
        ret , frame = self.cam.read()
        if ret == True:
            # save video 
            if self.startVideo == True : 
                self.videoWritter.write(frame)

            # show 
            show = cv2.resize(frame,(800,800))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.videoLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))
            
    def closeEvent(self,event):
        if(self.cam.isOpened()):
            self.cam.release()
            self.videoWritter.release()
            
        if self.timerCamera.isActive():
            self.timerCamera.stop()
            
        event.accept()
            
            
if __name__ == "__main__":
    #init 
    app = QApplication(sys.argv)
    
    #config 
    host = tryHost()
    host.show()
    
    #begin 
    sys.exit(app.exec_())
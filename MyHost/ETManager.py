#!/usr/bin/env python3
# -*- coding: UTF-8 -*- 

# note: close fcntl (in 3 pos)

import os
#import fcntl
import select
import socket
import sys
import json
import datetime
import threading
import time
import errno
import pandas
import base64
import numpy as np 
import cv2 

class ETManager:
    ASK_DATA = 1
    ASK_IMG = 6 
    EVT_ASK = 101;
    askMethod = [0, 1, 2, 3]
    
    def __init__(self,appHost="127.0.0.1" ,appPort=9011,appImgPort=9013):
        # basic info  
        self.appHost = appHost
        self.appPort = appPort       
        self.appImgPort = appImgPort
        
        # app connction 
        self.appClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = False
        
        # img connection 
        self.appImgClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.imgConn = False 
        
        # app thread 
        self.thread = threading.Thread(target=self.recvFromApp,args=())
        self.threadFlag = False
        
        # img thread 
        self.imgThread = threading.Thread(target=self.recvFromImg,args=())
        self.imgThreadFlag = False 
        
        # output eye pos 
        self.eyePosX = 0
        self.eyePosY = 0  
    
        # output img  
        self.totallen = 0 
        self.dataBuffer = bytearray()
        self.frameBuffer = bytearray()
        
        self.img = np.zeros((640,480,3), np.uint8)    
        
             
    #-----    fundamental function    -----# 
    def packEvent(self, cmd, how):
        json = {};
        json['ty'] = self.EVT_ASK;
        json['id'] = 1;
        json['ts'] = int(datetime.datetime.now().timestamp()*1000);	# ms
        json['cmd'] = cmd;
        json['how'] = how;
        return json
    
    #-----    basic function    -----------# 
    def connectToApp(self, server_addr):
        self.appClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.appClient.connect(server_addr)
        #fcntl.fcntl(self.appClient, fcntl.F_SETFL, os.O_NONBLOCK)
        self.conn = True
    
    def connectToImg(self,imgAddr):
        self.appImgClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.appImgClient.connect(imgAddr)
        #fcntl.fcntl(self.appImgClient,fcntl.F_SETFL,os.O_NONBLOCK)
        self.imgConn = True
    
    def sendToApp(self, how):
        msg = json.dumps(self.packEvent(self.ASK_DATA, how))
        msg += "\n"
        self.appClient.sendall(msg.encode())
        if(__debug__):
            print("sent msg to app: " + msg)
            
    def sendToImg(self,how):
        msg = json.dumps(self.packEvent(self.ASK_IMG,how))
        msg += "\n"
        self.appClient.sendall(msg.encode())
        print("sent msg to app: " + msg)
    
    def recvFromApp(self):        
        while(self.threadFlag):
            try:
                ready = select.select([self.appClient], [], [], 2)	# timeout: 2 seconds
                if ready[0]:
                    data = self.appClient.recv(4096)        
                    if(len(data)):
                        # data process
                        dataFrame = pandas.read_json(data.decode("utf-8"),lines = True)
                        if(__debug__):
                            print("Got msg from APP:\n")
                            print(dataFrame)
                       
                        # mean of data      
                        self.eyePosX = dataFrame["x"].mean()
                        self.eyePosY = dataFrame["y"].mean()
                        if(__debug__):
                            print("\n Eye location:")
                            print("    x :",self.eyePosX)
                            print("    y :",self.eyePosY)
                            print("\n")
                        
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    time.sleep(1)
            except:
                pass 
            
            time.sleep(0.1)
        if(__debug__):
            print("End data recv.\n")
            
    def recvFromImg(self):
        while(self.imgThreadFlag):
            try:
                print("one try on select")
                ready = select.select([self.appImgClient], [], [], 2)	# timeout: 2 seconds
                if ready[0]:
                    data = self.appImgClient.recv(614400)
                    print("data len: ",len(data))

                    #if not empty 
                    if len(data):
                        #append all data 
                        self.dataBuffer.extend(data)
                        print("append all data done")
                        #update info 
                        
                        if(self.totallen == 0):
                            self.updateInfo()
                            print("update info done") 

                        # update new frame 
                        if(len(self.dataBuffer) >= self.totallen):
                            self.updateFrame() 
                            print("update new frame done")

            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    time.sleep(1)
                print("got socket exception:" + str(e))
            except BaseException as b:
                print("other exception: "+ str(b))
                print("lost all frame") 
                self.dataBuffer = bytearray()
                self.totallen = 0 
                pass 
           #print("No data")
            time.sleep(0.1)
        
    def updateInfo(self):
        if(len(self.dataBuffer)>0 and self.dataBuffer[0] == 0xFE and self.dataBuffer[1] == 0xA5 and self.dataBuffer[2] == 0x5A and self.dataBuffer[3] == 0xEF):
            self.totallen = (self.dataBuffer[4]<<24) + (self.dataBuffer[5]<<16) + (self.dataBuffer[6]<<8) + self.dataBuffer[7] + 1
        else:
            if(__debug__):
                print("update buffer info fail!")
                print("now buffer length is :",len(self.dataBuffer)) 
                print("begin correct")
                
                dataBegin = 0 
                #correct
                while True: 
                    if self.dataBuffer[dataBegin] == 0xFE and self.dataBuffer[dataBegin+1] == 0xA5 and self.dataBuffer[dataBegin + 2] == 0x5A and self.dataBuffer[dataBegin + 3] == 0xEF:
                        break 
                    else: 
                        dataBegin = dataBegin + 1
                          
                self.dataBuffer = self.dataBuffer[dataBegin:]
            
    def updateFrame(self):
        self.frameBuffer = self.dataBuffer[:self.totallen]
        self.dataBuffer = self.dataBuffer[self.totallen:]
        
        self.totallen = 0 
        self.updateInfo()
       
        self.preImg()
        
        # only for test  
        # self.showImg()
        
    def preImg(self):
        #print("pre Img begin")
        
        if(self.frameBuffer[0] == 0xFE and self.frameBuffer[1] == 0xA5 and self.frameBuffer[2] == 0x5A and self.frameBuffer[3] == 0xEF):
            #print("real frame")
            totallen = (self.frameBuffer[4]<<24) + (self.frameBuffer[5]<<16) + (self.frameBuffer[6]<<8) + self.frameBuffer[7] + 1
            pos = 10 
            jsonLen = (self.frameBuffer[8]<<8) + self.frameBuffer[9]
            jsonStr = self.frameBuffer[pos:pos + jsonLen].decode("utf-8")
            jsonData = json.loads(jsonStr)
            imageType = jsonData['image']
            
            if imageType == 3 :
                #print("right image Type")
                img = self.frameBuffer[pos+jsonLen:totallen]
                imgB64_Decode = base64.b64decode(img)
                img_np = np.fromstring(imgB64_Decode,np.uint8)
                self.img = cv2.imdecode(img_np,cv2.COLOR_BGR2RGB)
                
            else: 
                print("image Type wrong: ",imageType)
        
    def showImg(self):
        cv2.imshow('img',self.img)
        cv2.waitKey(500)
        cv2.destroyAllWindows()
        
    #-----------    higher func    ---------------#

    # start: 
    #       start app, thread, and data 
    # in:   none 
    # out:  none 
    def start(self):
        try:
            #client conn 
            if(self.conn == False):
                print('Connecting to %s port %s' %(self.appHost,self.appPort),end='',flush=True)
                self.connectToApp((self.appHost,self.appPort))
                print('Done')
                
                # begin thread 
                if(self.threadFlag == False):
                    self.threadFlag = True
                    self.thread.start()
                    
                # begin data 
                self.sendToApp(self.askMethod[1])
    
                # begin image 
                self.sendToImg(self.askMethod[3])
                if(self.imgConn == False):
                    self.connectToImg((self.appHost,self.appImgPort))
                    print("Connection to %s port %s "%(self.appHost,self.appImgPort),end= '',flush= True)
                    if(self.imgThreadFlag ==False):
                        self.imgThreadFlag = True
                        self.imgThread.start()
    
        except socket.error as e:
            print("Connnect refused by  " + self.appHost)
            self.conn = False 
    
        except BaseException as e: 
            print("Other Error: " + str(e))


    # eyePos: 
    #       return eye pos in pic 
    # in:   none 
    # out:  x , y 
    def eyePos(self):
        return self.eyePosX,self.eyePosY

    # getImage:
    #       return realtime img (in opencv format)
    # in:   none 
    # out:  img (in numpy/opencv format)
    def getImage(self):
        return self.img
        
         
    # close: 
    #       close data, app, and thread 
    # in:   none 
    # out:  none 
    def close(self):
        # close data 
        self.sendToApp(self.askMethod[0])
        print("send to app done")
        
        # join thread 
        self.threadFlag = False 
        self.thread.join()
        print("thread join done")
        
        #close img data 
        self.sendToImg(self.askMethod[3])
        print("sent to img done")
        
        #join image thread 
        self.imgThreadFlag = False
        self.imgThread.join()
        print("img thread join done")
        
        #close img client 
        self.appImgClient.close()
        self.imgConn = False
        
        #close app client 
        self.appClient.close()
        self.conn = False 
        print("appclient close done")
        
        
        


import cv2 
import math 
import numpy as np 
import copy 

# to use this module 
# first : use the ImgOutline 
# then : use the find Contours/ box 
# finally : perspective trans , get result img 

def inverseImg(img):
    height , width = img.shape  
    
    for row in range(height):
        for wid in range(width):
            img[row,wid] = 255 - img[row,wid]
            
    return img 

#
def ImgOutline(oriImg):
    # gray img 
    grayImg = cv2.cvtColor(oriImg,cv2.COLOR_BGR2GRAY)
    
    # boolen 
    ret,grayImg = cv2.threshold(grayImg, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    # gaussian 
    blurred = cv2.GaussianBlur(grayImg , (5,5) , 0)
    blurred = inverseImg(blurred)
    
    _ , RedThresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    
    #close 
    closed = cv2.morphologyEx(RedThresh, cv2.MORPH_CLOSE, kernel)
    #open 
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel) 
    
    return oriImg , grayImg , RedThresh , closed , opened 


# find contours: 
#   find rect contour
#   in:     oriImg, opened  
#   out:    box , drawImg
#       (if not find)  return [], oriImg

def findContours(oriImg , opened):
    image, contours, hierarchy = cv2.findContours(opened, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    approxContours = [] 
    
    # approx contours 
    for cnt in contours: 
        epsilon = 0.1*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        if len(approx) == 4 :
            approxContours.append(cnt)
            
            
    #check contour detected 
    #contour_img = cv2.imread("blank.png")
    #contour_img = cv2.resize(contour_img,image.shape)
    #cv2.drawContours(contour_img,contours,-1, (0,0,0), 3)
    #cv2.imshow('contour img',contour_img)
    
    #no contour find  
    if len(approxContours) == 0:
        #print("no contours find")
        return approxContours,oriImg
    
    # find max contour
    c = sorted(approxContours, key=cv2.contourArea, reverse=True)[0] 
    epsilon = 0.1*cv2.arcLength(c,True)
    c_approx = cv2.approxPolyDP(c,epsilon,True)
    #print("c approx")
    #print(c_approx)
    
    # get box 
    left_up = c_approx[0][0]
    right_up = c_approx[1][0]
    left_down = c_approx[2][0]
    right_down = c_approx[3][0]
    
    tmp = np.vstack((left_up,right_up,left_down,right_down))
    convertValue = [0,0]
    
    for i in range(3):
        min = i 
    
        for j in range(i,4):
            if(tmp[j][1] < tmp[min][1]):
                min = j 

        if(min != i):
            convertValue = copy.deepcopy(tmp[min])
            tmp[min]=tmp[i]
            tmp[i] = copy.deepcopy(convertValue)
        

    if(tmp[0][0]>tmp[1][0]):
        convertValue = copy.deepcopy(tmp[0])
        tmp[0] = tmp[1]
        tmp[1] = copy.deepcopy(convertValue)
    
    if(tmp[2][0]>tmp[3][0]):
        convertValue = copy.deepcopy(tmp[2])
        tmp[2] = tmp[3]
        tmp[3] = copy.deepcopy(convertValue)
        
    left_up = tmp[0]
    right_up = tmp[1]
    left_down = tmp[2]
    right_down = tmp[3]
    
    box= np.vstack((left_up,right_up,left_down,right_down))
    #print("after sorted [box]:")
    #print("box[0]:", box[0])
    #print("box[1]:", box[1])
    #print("box[2]:", box[2])
    #print("box[3]:", box[3])
    
    #draw  approx contour 
    drawImg = cv2.drawContours(oriImg.copy(), c_approx, -1, (0, 0, 255), 3)
    
    return box , drawImg 

# perspective transformation 
#   in:     box, oriImg 
#   out:    result Img 
def perspectiveTrans(box,oriImg):
    # get original shape 
    H_rows, W_cols= oriImg.shape[:2]

    # cal trans matrix 
    pts1 = np.float32([box[0], box[1], box[2], box[3]])
    pts2 = np.float32([[0, 0],[800,0],[0, 800],[800,800],])     # here need to change ? 

    # cal Trans matrix , result img 
    M = cv2.getPerspectiveTransform(pts1, pts2)
    result_img = cv2.warpPerspective(oriImg, M, (800,800))

    return result_img    

def getTransMat(box,oriImg):
    # get original shape 
    H_rows, W_cols= oriImg.shape[:2]

    # cal trans matrix 
    pts1 = np.float32([box[0], box[1], box[2], box[3]])
    pts2 = np.float32([[0, 0],[800,0],[0, 800],[800,800],])     # here need to change ? 

    # cal Trans matrix , result img 
    M = cv2.getPerspectiveTransform(pts1, pts2)   
    
    return M  

if __name__ == "__main__":
    input_dir = "../rectify/try.png"
    oriImg = cv2.imread(input_dir)
    
    #first 
    oriImg , grayImg , RedThresh , closed , opened = ImgOutline(oriImg)
    
    #second 
    box , drawImg = findContours(oriImg , opened)
    
    #final 
    resultImg = perspectiveTrans(box,oriImg)
    
    
    #show 
    cv2.imshow("original",oriImg)
    cv2.imshow("gray",grayImg)
    cv2.imshow("closed",closed)
    cv2.imshow("opened",opened)
    cv2.imshow("drawImg",drawImg)
    cv2.imshow("result",resultImg)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

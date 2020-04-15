'''
detecNote

Roxane Carraux
Francois Bouthillier de Beaumont
Loïc Jurasz

'''

# imports
import cv2
import glob
import sys
import numpy as np

def analyse(img):
    # detect circle
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 120)
    lines = cv2.HoughLinesP(edges, 1, np.pi/360, 80, None, 1, 1)
    for line in lines:
        pt1 = (line[0][0],line[0][1])
        pt2 = (line[0][2],line[0][3])
        cv2.line(img, pt1, pt2, (255,255,255), 2)
    
    '''
    circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=0)

    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
    '''
    #cv2.imshow('detected circles',cimg)
    cv2.imshow("canny", gray)
    cv2.imshow("image de depart", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    filenames = [img for img in glob.glob("Images/exempleMe2.png")]
    for f1 in filenames:
        img = cv2.imread(f1)
        analyse(img)

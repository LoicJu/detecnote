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
'''
from skimage import data, color, img_as_ubyte
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter
'''
def analyse(img):
    # we resize because the image was too big
    img = cv2.resize(img,(int(img.shape[1]*0.4),int(img.shape[0]*0.4)),interpolation = cv2.INTER_AREA)
    result = img.copy()
    # lines
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Detect horizontal lines
    # lines are ordered from bottom to top
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,1)) # 20,1 will not take the short lines
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts_hor = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_hor = cnts_hor[0] if len(cnts_hor) == 2 else cnts_hor[1]
    for c in cnts_hor:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    # Detect vertical lines
    # lines are ordered from bottom to top, right to left
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,20))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts_ver = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_ver = cnts_ver[0] if len(cnts_ver) == 2 else cnts_ver[1]
    #TODO doesn't work
    # we add a vertical line between the 2 last one to separate the keys (clé de fa, clé de sol) from the notes
    '''
    vert_pix=abs(cnts_ver[-1][0][0][0]-cnts_ver[-2][0][0][0])+cnts_ver[-2][0][0][0]
    additional_line = [[[vert_pix, cnts_ver[-2][0][0][1]],[vert_pix,cnts_ver[-2][1][0][1]],[vert_pix,cnts_ver[-2][2][0][1]],[vert_pix,cnts_ver[-2][3][0][1]]]]
    cnts_ver.append(additional_line)
    '''
    for c in cnts_ver:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    # our references lines will be cnts_hor[0][0][0][1] (bottom line) and cnts_hor[-1][0][0][1] (top horizontal line) and cnt_ver[0] (right line) and cnt_ver[-1] (left line)

    # TODO , take little lines
    '''
    # after we've put in blank every lines, we search the horizonzal lines that are from the notes (above or under a note)
    result1_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    _, result1_binary = cv2.threshold(result1_gray, 225, 255, cv2.THRESH_BINARY_INV)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,1)) # to take short lines
    detect_horizontal = cv2.morphologyEx(result1_binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts_hor_short = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_hor_short = cnts_hor_short[0] if len(cnts_hor_short) == 2 else cnts_hor_short[1]
    for c in cnts_hor_short:
        cv2.drawContours(result, [c], -1, (255,255,0), 2)

    # now we search verticale lines that are from notes like "noir" or "croche"
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5)) # 1,10 to take short lines
    detect_vertical = cv2.morphologyEx(result1_binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts_ver_short = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_ver_short = cnts_ver_short[0] if len(cnts_ver_short) == 2 else cnts_ver_short[1]
    for c in cnts_ver_short:
        cv2.drawContours(result, [c], -1, (0,255,255), 2)
    '''
    result_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    _, result_binary = cv2.threshold(result_gray, 225, 255, cv2.THRESH_BINARY_INV)
    # detect contour
    contours, hierarchy = cv2.findContours(result_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # draw all contours, contours have many hierarchie so we have to do a double for to enter all the hierarchies
    contours_finals = []
    for c in contours:
        for c2 in c:
            if not(c2[0][1] > cnts_hor[0][0][0][1] or c2[0][1] < cnts_hor[-1][0][0][1] or c2[0][0] > cnts_ver[0][0][0][0] or c2[0][0] < cnts_ver[-1][0][0][0]):
                contours_finals.append(c2)
    result = cv2.drawContours(result, contours_finals, -1, (0, 255, 0), 2)

    # circles NOT WORKING
    '''
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=30)
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(result,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(result,(i[0],i[1]),2,(0,0,255),3)
    '''
    # elliptic NOT WORKING
    '''
    image_gray = color.rgb2gray(img)
    edges = canny(image_gray, sigma=2.0,low_threshold=0.55, high_threshold=0.8)

    result1 = hough_ellipse(edges, accuracy=20, threshold=250,min_size=100, max_size=120)
    result1.sort(order='accumulator')

    best = list(result1[-1])
    yc, xc, a, b = [int(round(x)) for x in best[1:5]]
    orientation = best[5]

    cy, cx = ellipse_perimeter(yc, xc, a, b, orientation)
    result[cy, cx] = (0, 0, 255)
    edges = color.gray2rgb(img_as_ubyte(edges))
    edges[cy, cx] = (250, 0, 0)
    '''
    cv2.imshow('detected circles',result)
    cv2.imshow("image de depart", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    filenames = [img for img in glob.glob("Images/partition1_wbc.png")]
    for f1 in filenames:
        img = cv2.imread(f1)
        analyse(img)

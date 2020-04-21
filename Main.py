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

def analyse(img, nameimg):
    # we resize because the image was too big
    img = cv2.resize(img,(int(img.shape[1]*0.4),int(img.shape[0]*0.4)),interpolation = cv2.INTER_AREA)
    result_intermediate = img.copy()
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
    # Detect vertical lines
    # lines are ordered from bottom to top, right to left
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,20))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts_ver = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_ver = cnts_ver[0] if len(cnts_ver) == 2 else cnts_ver[1]

    # we add a vertical line between the 2 last one to separate the keys (clé de fa, clé de sol) from the notes
    vert_pix=int((abs(cnts_ver[-1][0][0][0]-cnts_ver[-2][0][0][0]))/2)+cnts_ver[-1][0][0][0]
    additional_line = np.array([[[vert_pix, cnts_ver[-2][0][0][1]],[vert_pix,cnts_ver[-2][1][0][1]],[vert_pix,cnts_ver[-2][2][0][1]],[vert_pix,cnts_ver[-2][3][0][1]]]])
    cnts_ver.append(additional_line)

    # we draw in red to see the intermediate result
    for c in cnts_hor:
        cv2.drawContours(result_intermediate, [c], -1, (0,0,255), 2)
    for c in cnts_ver:
        cv2.drawContours(result_intermediate, [c], -1, (0,0,255), 2)
    # our references lines will be cnts_hor[0][0][0][1] (bottom line) and cnts_hor[-1][0][0][1] (top horizontal line) and cnts_ver[0] (right line) and cnts_ver[-1] (left line, after the keys (clé de sol, clé de fa))
    
    # take little lines
    # we search the horizonzal lines that are from the notes (above or under a note)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,1)) # to take short lines
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts_hor_short = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_hor_short = cnts_hor_short[0] if len(cnts_hor_short) == 2 else cnts_hor_short[1]
    # cnts_hor_short_final will have all the little horizontal lines that interested us
    cnts_hor_short_final=[]
    for c in cnts_hor_short:
        # test if it's not part of the title (if it's just above the top horizontal line, it' ok) and if the line begin before or at the same place as an "classic" horizontal line, it's a long line so we don't take it
        if cnts_hor[-1][0][0][1]-20<c[0][0][1] and cnts_ver[-1][0][0][0]<c[0][0][0]:
            cnts_hor_short_final.append(c)
            cv2.drawContours(result_intermediate, [c], -1, (0,0,255), 2)
    cv2.drawContours(result_intermediate,cnts_hor_short_final, -1, (0,255,255), 2)
    
    # now we search verticale lines that are from notes like "noir" or "croche"
    # cnts_ver_short_final will have all the little horizontal lines that interested us
    cnts_ver_short_final=[]
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,10)) # 1,10 to take short lines
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts_ver_short = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_ver_short = cnts_ver_short[0] if len(cnts_ver_short) == 2 else cnts_ver_short[1]
    for c in cnts_ver_short:
        # test if the length of the vertical line isn't too big (as classic vertical bar), then, test if it's bewteen the base lines
        if abs(c[0][0][1]-c[1][0][1])< abs(cnts_ver[-1][0][0][1]-cnts_ver[-1][0][1][1]) and cnts_ver[-1][0][0][0]<c[0][0][0] and cnts_hor[-1][0][0][1]-20<c[0][0][1]:
            cv2.drawContours(result_intermediate, [c], -1, (0,255,255), 2)
    # draw all vertical lines and horizontal lines in white
    for c in cnts_hor:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    for c in cnts_ver:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    # transform image to detect contours
    result_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    _, result_binary = cv2.threshold(result_gray, 225, 255, cv2.THRESH_BINARY_INV)
    # detect contour
    contours, hierarchy = cv2.findContours(result_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # we draw all the contour in white
    cv2.drawContours(result, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
    contours_finals = []
    for c in contours:
        # test if contours are between our lines
        if not(c[0][0][1] > cnts_hor[0][0][0][1] or c[0][0][1] < cnts_hor[-1][0][0][1] or c[0][0][0] > cnts_ver[0][0][0][0] or c[0][0][0] < cnts_ver[-1][0][0][0]):
            # we add the contours that are between our lines in contours_final
            contours_finals.append(c)
    # we draw contours final
    result = cv2.drawContours(result, contours_finals, -1, (0, 255, 0), thickness=cv2.FILLED)

    cv2.imshow('lines',result_intermediate)
    cv2.imshow('detected contours',result)
    cv2.imshow("image de depart", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # write in file what are the notes TODO
    f= open(nameimg + ".txt","w+")
    f.write("hello")
    f.close()

if __name__ == "__main__":
    filenames = [img for img in glob.glob("Images/partition1_wbc.png")]
    for f1 in filenames:
        img = cv2.imread(f1)
        analyse(img, f1)

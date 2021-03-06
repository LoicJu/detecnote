'''
detecNote

Roxane Carraux
Bouthillier
Loïc Jurasz

'''

# imports
import cv2
import glob
import sys
import numpy as np
from PIL import Image

SHOW_IMAGE = True
HAS_TRANSPARENT_BC = True

def analyse(img, fullname, nameimg):
    if HAS_TRANSPARENT_BC:
        img_tr = Image.open(fullname)
        background = Image.new("RGB", img_tr.size, (255, 255, 255))
        background.paste(img_tr, mask=img_tr.split()[3])
        img = np.array(background)
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
    cv2.drawContours(result_intermediate,cnts_hor_short_final, -1, (0,255,255), 2)
    
    # now we search verticale lines that are from notes like "noir" or "croche"
    # cnts_ver_short_final will have all the little vertical lines that interested us
    cnts_ver_short_final=[]
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,10)) # 1,10 to take short lines
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts_ver_short = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_ver_short = cnts_ver_short[0] if len(cnts_ver_short) == 2 else cnts_ver_short[1]
    for c in cnts_ver_short:
        # test if the length of the vertical line isn't too big (as classic vertical bar), then, test if it's bewteen the base lines
        if abs(c[0][0][1]-c[1][0][1])< abs(cnts_ver[-1][0][0][1]-cnts_ver[-1][0][1][1]) and cnts_ver[-1][0][0][0]<c[0][0][0] and cnts_hor[-1][0][0][1]-20<c[0][0][1]:
            cnts_ver_short_final.append(c)
    cv2.drawContours(result_intermediate, cnts_ver_short_final, -1, (0,255,255), 2)

    # draw all vertical lines and horizontal lines in white
    for c in cnts_hor:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    for c in cnts_ver:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    for c in cnts_hor_short_final:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)
    for c in cnts_ver_short_final:
        cv2.drawContours(result, [c], -1, (255,255,255), 2)

    # detect the highest horizontal line
    highest_hor_line = cnts_hor[-1][0][0][1]
    for c in cnts_hor_short_final:
        if c[0][0][1]<cnts_hor[-1][0][0][1]:
            highest_hor_line = c[0][0][1]
    # detect the lowest horizontal line
    lowest_hor_line = cnts_hor[0][0][0][1]
    for c in cnts_hor_short_final:
        if c[0][0][1]>cnts_hor[0][0][0][1]:
            lowest_hor_line = c[0][0][1]
    # we detect the rightest vertical line
    rightest_vert_line = cnts_ver[-1][0][0][0]
    for c in cnts_ver:
        if c[0][0][0]<cnts_ver[0][0][0][0]:
            rightest_vert_line = c[0][0][0]
    # there is no need to detect the leftest vertical line as we'll use cnts_ver[0][0][0][0] because it's the line that we add to take out the keys
    # transform image to detect contours
    result_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    _, result_binary = cv2.threshold(result_gray, 225, 255, cv2.THRESH_BINARY_INV)
    # detect contour
    contours, hierarchy = cv2.findContours(result_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # we draw all the contour in white
    cv2.drawContours(result, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
    contours_finals = []
    for c in contours:
        # test if contours are between our lines (first if it's not below, second if it's not higher, third not to the right, fourth to te left)
        if not((c[0][0][1] > lowest_hor_line+20) or (c[0][0][1] < highest_hor_line-20) or (c[0][0][0] > cnts_ver[0][0][0][0]) or (c[0][0][0] < rightest_vert_line)):
            # we add the contours that are between our lines in contours_final
            contours_finals.append(c)
    # we draw contours final
    cv2.drawContours(result, contours_finals, -1, (255, 0, 0), thickness=cv2.FILLED)

    # we dilate the image result and erode it, we can get off of some points that were there and we have entire notes
    result_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    _, result_binary = cv2.threshold(result_gray, 225, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((8,8),np.uint8)
    result_binary = cv2.dilate(result_binary, kernel)
    kernel = np.ones((11,11),np.uint8)
    result_binary = cv2.erode(result_binary, kernel)

    # now we only have the entire notes
    contours_notes, hierarchy = cv2.findContours(result_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # order contours_notes from right to left
    contours_notes.sort(key=lambda x : x[0][0][0], reverse=True)
    # we create an array with the notes in it
    notes = ['Do ','Re ','Mi ','Fa ','Sol ','La ','Si ']
    # we can know which note is which with the lines, we know that the long lines are grouped by 5
    lines = []
    # if it's a "clé de sol" or "clé de fa" we begin with a "clé de sol" as we begin from the bottom
    keys = 0
    for i in range(0, len(cnts_hor)-1, +5):
        if keys != 0:
            keys = 0
        else :
            keys = 2
        lines.append("\n")
        # we'll add little lines in this list
        cnts_hor_littles = cnts_hor.copy()
        # each note
        for c2 in contours_notes:
            # need to check for little lines, above or under the 5 principal lines
            nbLines = 5
            nbLinesUnder = 0
            aboveLine = cnts_hor[i+4][0][0][1]
            line_to_add_above = cnts_hor[i+4]
            underLine = cnts_hor[i][0][0][1]
            line_to_add_below = cnts_hor[i]
            insert_above = False
            insert_under = False
            # under
            for clittles in cnts_hor_short:
                if clittles[0][0][1] > underLine and clittles[0][0][1] < underLine+20:
                    underLine = clittles[0][0][1]
                    line_to_add_below = clittles
                    insert_under = True
            if insert_under:
                nbLines += 1
                nbLinesUnder += 1
                cnts_hor_littles.insert(i,line_to_add_below)
             # above
            for clittles in cnts_hor_short:
                if clittles[0][0][1] < aboveLine and clittles[0][0][1] > aboveLine-20:
                    aboveLine = clittles[0][0][1]
                    line_to_add_above = clittles
                    insert_above = True
            if insert_above:
                nbLines += 1
                cnts_hor_littles.insert(i+5,line_to_add_above)
            # if the note is between the 5 lines + and - 15 is to take the notes that are just above or under the line
            if c2[0][0][1]<underLine+15 and c2[0][0][1]>aboveLine-15:
                # we put this variable that will help us locate the note
                above = 0
                # if it's on the line
                on_line = False 
                # if the note has a vertical line
                has_vert_line = False 
                # we parcour the lines 
                for j in range(0, nbLines):
                    above_the_line = False
                    under_the_line = False 
                    # we parcour all the points in the contours to compare to the line in order to know if it's above and under the line (if it's on the line)       
                    for c3 in c2:
                        # we test if the contour is under the line
                        if c3[0][1]>cnts_hor_littles[j+i][0][0][1]:
                            under_the_line = True
                        # we test if the contour is above the line
                        if c3[0][1]<cnts_hor_littles[j+i][0][0][1]:
                            above_the_line = True
                        # if it's under and above, it's on the line
                        if under_the_line and above_the_line:
                            on_line = True
                        # test all the contour of little vertical line
                        for v1 in cnts_ver_short_final :
                            # test if the vert line is between the lines
                            if v1[0][0][1]<underLine+15 and v1[0][0][1]>aboveLine-15:
                                # test if the note and the vertical lines are close enough
                                if abs(c3[0][0]-v1[0][0][0]) < 10:
                                    has_vert_line = True
                    if c2[0][0][1]<cnts_hor_littles[j+i][0][0][1]:
                       above += 1 
                # write in lines what notes it is
                # ['Do','Re','Mi','Fa','Sol','La','Si']
                if on_line:
                    lines.append(notes[((2*above-2*nbLinesUnder)+keys)%7]) 
                else:
                    lines.append(notes[(2*above-2*nbLinesUnder+1+keys)%7])
                if has_vert_line:
                    lines.append('(n/b)')
                else:
                    lines.append('(r)')                
            if insert_above:
                cnts_hor_littles.pop(i+5)
            if insert_under:
                cnts_hor_littles.pop(i)
    lines.reverse()
    # write in file what are the notes
    f= open(nameimg + ".txt","w+")
    for n in lines:
        f.write(n)
    f.close()

    if SHOW_IMAGE:
        cv2.imshow("image de depart", img)
        cv2.imshow('contours détéctés',result)
        cv2.imshow('contour binaire',result_binary)
        cv2.imshow('Detection de lines',result_intermediate)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    filenames = [img for img in glob.glob("Images/*.png")]
    for f1 in filenames:
        img = cv2.imread(f1)
        txt = f1.split('\\', 1)
        txt = txt[1].split('.')
        txt = txt[0]
        txt  = "Resultat\\" + txt
        analyse(img, f1, txt)

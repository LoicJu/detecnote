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

def analyse(img):
    cv2.imshow("image de départ", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    filenames = [img for img in glob.glob("Images/*.png")]
    for f1 in filenames:
        img = cv2.imread(f1)
        analyse(img)

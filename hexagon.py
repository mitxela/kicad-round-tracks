from PIL import Image
from math import *
import os
import subprocess
import numpy as np

three69 = sqrt(3);
thickness = 28;
unit_size = 25;
proximity = 13;

box_length = unit_size*3;
box_height = unit_size*2*sin(radians(60));

def processImage(filename):
    #gerb = Image.open(filename);
    #gerbpix = gerb.getdata();

    # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
    #img = Image.new( 'L', (gerb_width,gerb_height), "white").tobytes() # create a new white image
    newimdata = []
    #pixels = Image.open(filename).convert('LA') # create the pixel map, convert to greyscale
    img = Image.open( filename ).convert('L')
    gerb_width, gerb_height = img.size;
    img.load()
    pixels = np.rot90(np.asarray( img, dtype="int8" ))

    print(gerb_width)
    print(gerb_height)
    # one unit box looks like
    # _    _
    #  \__/
    #  /  \

    # if the quadrant is normalized (flip symmetry), each section looks like
    # _
    #  \_
    #
    # where both horizontal lines are unitsize/2 long

    for y in range(gerb_height):    # For every row
        print( float(y)/gerb_height );
        for x in range(gerb_width):    # for every col:
            #print(pixels[x, y])
            #print(gerb_width)
            # find relative location within box
            ypos = y % box_height;
            xpos = x % box_length;
            # normalize quadrant
            if (ypos > box_height/2):
                ypos = box_height - ypos;
            if (xpos > box_length/2):
                xpos = box_length - xpos;
            
            
            # warning track, or standard hexagon
            if (
                (not square_detect(x,y, proximity, gerb_width, gerb_height, pixels))
                and
                (square_detect(x,y, proximity + thickness, gerb_width, gerb_height, pixels)
                or
                (xpos < unit_size/2 and ypos < thickness/2) # top line
                or
                (xpos > (box_length - unit_size)/2 and ypos > (box_height - thickness)/2) # bottom line
                or
                (abs(ypos - three69*(xpos - unit_size/2)) < thickness) # diagonal defined by y = .5sqrt(3)(x - unit)
                )):
                newimdata.append(0) # set the colour accordingly
            else:
                newimdata.append(1) # set the colour accordingly
			    

    #img.show()
    img = Image.new(pixels.mode,pixels.size)
    img.putdata(newimdata)
    img.save(filename + '.bmp')



# square detection for simplicity
def square_detect(x, y, width, gerb_width, gerb_height, gerbpix):
    #keep min values on image
    xmin = x - width;
    if xmin < 0:
        xmin = 0;
    ymin = y - width;
    if ymin < 0:
        ymin = 0;
		
    #keep max values on image
    xmax = x + width;
    if xmax >= gerb_width:
        xmax = gerb_width-1;
    ymax = y + width;
    if ymax >= gerb_height:
        ymax = gerb_height-1
		
    # allow to skip 5 pixels. assumes 8 pix width
    # horizontals
    for thisx in range(xmin, xmax, 5):
        if (gerbpix[thisx, ymin] != 0 or
            gerbpix[thisx, ymax] != 0):
            return True;
        
    # verticals
    for thisy in range(ymin, ymax, 5):
        if (gerbpix[xmin, thisy] != 0 or
            gerbpix[xmax, thisy] != 0):
            return True;
        
    return False;
        
# for all files in this dir
for file in os.listdir("."): 
    if file.endswith(".svg"): #if they are svg
        #convert to png
        sysString = "inkscape -z " + file + " -d 1600 -e " + file + ".bmp"
        print(sysString)
        print(subprocess.call(sysString))
        #process the new png
        processImage(file + ".bmp")

#this code is messy but i'm feeling lazy. don't judge

import os, datetime, re, random, numpy, operator, cv2
from sklearn.cluster import KMeans
from PIL import Image, ImageDraw

#create a list of all non-hidden files in input folder
def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

#create list of images in "input" directory
input_files = listdir_nohidden(os.getcwd()+'/input')

#for every image in file list
for i in input_files:

    #print state to terminal
    print("starting "+i)

    #define height of palette squares
    palette_height = 168

    #open image and record size
    old_im = Image.open('input/'+i)
    old_im = old_im.convert('RGB')
    old_size = old_im.size
    old_x = old_size[0]
    old_y = old_size[1]

    #scale the image to have a 40 px buffer whether landscape or portrait
    scale = old_x/float(1000)
    small_y = int(old_y/scale)

    #if y axis is too big to provide enough room underneath for blur
    #set up image for portrait 'mode'
    if small_y > (960-palette_height):
        new_scale = old_y/float(1000)
        small_im = old_im.resize((int(old_x/new_scale),1000), Image.ANTIALIAS)
        aspect = "portrait"
        #if there won't be enough room to right of image for portrait mode blur
        #escape and provide warning message
        if small_im.size[0] > (960-palette_height):
            print("ya gonna have to crop this bad boi")
            break
    #else we're gonna be working in landscape
    else:
        small_im = old_im.resize((1000,small_y), Image.ANTIALIAS)
        aspect = "landscape"

    #get small_im into a cv2 compatible format
    image = numpy.array(small_im)
    #reshape image into a list of pixels
    px_list = image.reshape((image.shape[0] * image.shape[1], 3))

    #run kmeans function
    clt = KMeans(n_clusters = 5)
    clt.fit(px_list)

    #get list of cluster colours
    clus_colours = clt.cluster_centers_.astype("uint8").tolist()

    #create background image (white)
    new_im = Image.new("RGB", (1080,1080),(255,255,255))

    #define where to paste small_im
    x_paste = 40
    y_paste = 40

    #paste small_im onto background new_im
    new_im.paste(small_im,(x_paste,y_paste))

    #draw palette squares and fill with cluster colours
    draw = ImageDraw.Draw(new_im)
    if aspect == "landscape":
        draw.rectangle([40,872,208,1040], fill=tuple(clus_colours[0]), outline=None)
        draw.rectangle([248,872,416,1040], fill=tuple(clus_colours[1]), outline=None)
        draw.rectangle([456,872,624,1040], fill=tuple(clus_colours[2]), outline=None)
        draw.rectangle([664,872,832,1040], fill=tuple(clus_colours[3]), outline=None)
        draw.rectangle([872,872,1040,1040], fill=tuple(clus_colours[4]), outline=None)
    else:
        draw.rectangle([872,40,1040,208], fill=tuple(clus_colours[0]), outline=None)
        draw.rectangle([872,248,1040,416], fill=tuple(clus_colours[1]), outline=None)
        draw.rectangle([872,456,1040,624], fill=tuple(clus_colours[2]), outline=None)
        draw.rectangle([872,664,1040,832], fill=tuple(clus_colours[3]), outline=None)
        draw.rectangle([872,872,1040,1040], fill=tuple(clus_colours[4]), outline=None)

    #get modified date of original photo - this allows the easy sorting of the
    #output files by age of the original
    mtime = os.path.getmtime(os.getcwd()+'/input/'+i)
    str_mtime = datetime.datetime.isoformat(datetime.datetime.fromtimestamp(mtime))
    str_mtime = re.sub("[^0-9.]", "-", str_mtime)

    #save the new image and prefix name with modified date
    new_im.save('output/'+str_mtime+'_'+i)

    #print state to terminal
    print(i+' converted')

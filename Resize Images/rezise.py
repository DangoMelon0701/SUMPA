import os
from PIL import Image

basewidth =3000

img_list = [ imfile for imfile in os.listdir(os.getcwd()) if imfile.endswith('.JPG')]

img_dir = os.path.join(os.getcwd(),'resized')
if not os.path.exists(img_dir):
    os.mkdir(img_dir)

for image_file in img_list:
    img = Image.open(image_file)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(os.path.join(img_dir,'{}.jpg'.format(image_file[:-4])))
### Script to edit capture date according to timestamp ###

import os
from datetime import datetime
import piexif

wkdir = os.path.split(__file__)[0]
bereal_saved_dir = os.path.join(wkdir, "BeReal_saved")

files = os.listdir(bereal_saved_dir)
files= sorted(files, reverse=True)
for i_file in files:
    i_file = os.path.join(bereal_saved_dir,i_file)
    exif_dict = piexif.load(i_file)

    # images are usually namend something like: bereal-2022-06-13-0823
    new_date = datetime.strptime(os.path.split(i_file)[1][7:22],"%Y-%m-%d-%H%M").strftime("%Y:%m:%d %H:%M:%S")

    exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, i_file)
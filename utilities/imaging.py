from wand.image import Image
import os

from utilities.common import utc_now_ts as now
from settings import UPLOAD_FOLDER

def thumbnail_process(file, content_type, content_id, sizes=[("sm", 50), ("lg", 75), ("xlg", 200)]):
    image_id = now()
    filename_template = content_id + '.%s.%s.png'
    
    # original
    with Image(filename=file) as img:
        crop_center(img)
        img.format = 'png'
        img.save(filename=os.path.join(UPLOAD_FOLDER, content_type, filename_template % (image_id, 'raw')))
        
    # sizes
    for (name, size) in sizes:
        with Image(filename=file) as img:
            crop_center(img)
            img.sample(size, size)
            img.format = 'png'
            img.save(filename=os.path.join(UPLOAD_FOLDER, content_type, filename_template % (image_id, name)))
            
    os.remove(file)
    return image_id
    
def crop_center(image):
    dst_landscape = 1 > image.width / image.height
    wh = image.width if dst_landscape else image.height
    image.crop(
        left=int((image.width - wh) / 2),
        top=int((image.height - wh) / 2),
        width=int(wh),
        height=int(wh)
    )
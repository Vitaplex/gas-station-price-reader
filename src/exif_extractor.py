import io
import json
from PIL import Image
from PIL.ExifTags import IFD, TAGS, GPSTAGS

def get_coords(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    exif_data = img.getexif()

    gps_info = exif_data.get_ifd(IFD.GPSInfo)
    if gps_info == {}: return None
    
    latitude = dms_to_decimal(gps_info.get(2), gps_info.get(1))
    longitude = dms_to_decimal(gps_info.get(4), gps_info.get(3))

    return latitude, longitude

def dms_to_decimal(dms, ref):
    degrees, minutes, seconds = dms
    decimal = float(degrees + (minutes / 60) + (seconds / 3600))
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal
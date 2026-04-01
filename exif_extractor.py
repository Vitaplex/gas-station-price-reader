from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_coords(image_path):
    img = Image.open(image_path)
    exif_data = img._getexif()

    gps_info = {}
    for key, value in exif_data.items():
        tag = TAGS.get(key)
        if tag == "GPSInfo":
            for t in value:
                sub_tag = GPSTAGS.get(t)
                gps_info[sub_tag] = value[t]

    def to_decimal(dms, ref):
        d, m, s = dms
        dec = d + m/60 + s/3600
        return -dec if ref in ["S", "W"] else dec

    lat = to_decimal(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
    lon = to_decimal(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])

    return lat, lon
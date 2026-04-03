import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

class ImageConverter:
    def get_image_bytes(self, image:bytes):
        data_str = image.decode()
        header, encoded = data_str.split(",", 1)
        bytearr = base64.b64decode(encoded)
        return bytearr

    def load_image(self, image:bytes):
        nparr = np.frombuffer(self.get_image_bytes(image), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    
    def convert_to_cv2_image(self, image):
        nparr = np.frombuffer(image, np.uint8)
        cv2_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return cv2_image
    
    def convert_to_jpg(self, image: bytes) -> bytes:
        pilimg = Image.open(BytesIO(image))

        img_rgb = pilimg.convert("RGB")
        exif_data = pilimg.info.get("exif")
        
        b = BytesIO()
        
        if exif_data is None:
            img_rgb.save(b, "JPEG")
        else:
            img_rgb.save(b, "JPEG", exif=exif_data)
        
        b.seek(0)
        
        return b.getvalue()

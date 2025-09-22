import pytesseract
import cv2
import numpy as np
import re
from PIL import Image, ImageEnhance, ImageOps
from Domain.Models import ProcessingParams, OCRSensorData

class OCRService:
    def __init__(self):
        pass
        
    def preprocess_image(self, image, params: ProcessingParams):
        # OpenCV to PIL
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = image
            
        # Convert to grayscale
        pil_image = pil_image.convert('L')
        
        # Apply image processing
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(params.contrast)
        
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(params.brightness)
        
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(params.sharpness)
        
        # Denoising
        if params.denoise > 0:
            img_array = np.array(pil_image)
            img_array = cv2.fastNlMeansDenoising(img_array, None, params.denoise, 7, 21)
            pil_image = Image.fromarray(img_array)
        
        # Thresholding
        if params.adaptive_thresh:
            img_array = np.array(pil_image)
            img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
            pil_image = Image.fromarray(img_array)
        else:
            pil_image = pil_image.point(lambda x: 0 if x < params.threshold else 255, '1')
        
        # Morphological operations
        if params.dilate > 1 or params.erode > 1:
            img_array = np.array(pil_image)
            kernel = np.ones((3, 3), np.uint8)
            
            if params.erode > 1:
                img_array = cv2.erode(img_array, kernel, iterations=params.erode - 1)
            
            if params.dilate > 1:
                img_array = cv2.dilate(img_array, kernel, iterations=params.dilate - 1)
                
            pil_image = Image.fromarray(img_array)
        
        # Inversion
        if params.invert:
            pil_image = ImageOps.invert(pil_image)
        
        return pil_image
        
    def extract_text(self, image, language='eng'):
        return pytesseract.image_to_string(image, lang=language, config='--psm 6')

    def parse_sensor_data(self, ocr_text: str):
        """OCR metninden sıcaklık verisini ayıklama"""
        # Metindeki sayısal değerleri bulmak için regex kullan (nokta veya virgül destekli)
        numbers = re.findall(r"[-+]?\d+[,.]?\d*", ocr_text.replace(',', '.'))
        
        if len(numbers) >= 1:
            try:
                # İlk bulunan sayıyı sıcaklık olarak kabul et
                temperature = float(numbers[0])
                # Yalnızca sıcaklık verisi döndür
                return OCRSensorData(temperature=temperature)
            except ValueError:
                return None
                
        return None
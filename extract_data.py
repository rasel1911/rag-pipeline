import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os 
import numpy as np
from PIL import ImageFilter, ImageEnhance



# Set custom config to whitelist characters
custom_config = r'--oem 3'

def enhance_image_for_ocr(image):
    gray = image.convert('L')
    contrast_enhancer = ImageEnhance.Contrast(gray)
    contrast = contrast_enhancer.enhance(2.0)
    sharp = contrast.filter(ImageFilter.SHARPEN)
    #binary = sharp.point(lambda x: 0 if x < 100 else 255, '1')
    return sharp


def pdf_to_images(pdf_path, dpi=300):
    pages = convert_from_path(pdf_path, dpi=dpi)
    enhanced_pages = []
    for i in range(len(pages)):
        if i>=4 and i<=18:
            crop = pages[i].crop((0, 300, pages[i].width, pages[i].height-400))
            enhanced_page = enhance_image_for_ocr(crop)
            enhanced_pages.append(enhanced_page)
    return enhanced_pages


def extract_text_from_images(images):
    full_text = ""
    for i, img in enumerate(images):
        if i == 0:
            pass
        else:
            print(f"Processing page {i+1}...")
            text = pytesseract.image_to_string(img, lang='ben', config=custom_config)  # 'ben' = Bengali
            clean_text = text.replace('\xa0', ' ')  # Remove non-breaking spaces
            clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])
            #clean_text = clean_text.replace('\n', ' ')
            #full_text += f"\n\n--- Page {i+1} ---\n\n{text}"
            full_text += clean_text
    return full_text



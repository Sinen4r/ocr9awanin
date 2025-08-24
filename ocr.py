import cv2
import numpy as np
from PIL import Image
import pdf2image
import pytesseract
import easyocr
import fitz  # PyMuPDF
import io
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
import re


class ArabicPDFOCR:
    def __init__(self, use_easyocr=True):
        self.use_easyocr = use_easyocr
        if use_easyocr:
            self.reader = easyocr.Reader(['ar'])  # Arabic and English
        
    def load_images_from_folder(self,folder, extensions=(".png", ".jpg", ".jpeg")):
        folder = Path(folder)
        image_files = sorted(
            [f for f in folder.iterdir() if f.suffix.lower() in extensions]
        )

        images = []
        for i, file in enumerate(image_files):
            print(f"Loading page {i+1}: {file.name}")
            img = Image.open(file)   
            images.append(img)

        return images
    def resize_from_bottom(self,img, new_height):
        h, w = img.shape[:2]
        if new_height >= h:
            return img  
        return img[:h - new_height, :]
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert PIL to OpenCV
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img = img_array
        
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Apply image enhancements
        # 1. Noise reduction
        gray=self.resize_from_bottom(gray,150)
        remove_watermark= self.remove_watermark(gray)

        denoised = cv2.fastNlMeansDenoising(remove_watermark)
        
        # 2. Threshold to get better black/white contrast
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 3. Morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite("cleaned.png", cleaned)

        return remove_watermark
    
    def ocr_with_tesseract(self, image):
        """Perform OCR using Tesseract"""
        try:
            config = r'--oem 3 --psm 6 -l ara+fra'
            
            # If image is numpy array, convert to PIL
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            text = pytesseract.image_to_string(image, config=config)
            return text.strip()
        except Exception as e:
            print(f"Tesseract OCR failed: {e}")
            return ""
    
    def ocr_with_easyocr(self, image):
        """Perform OCR using EasyOCR"""
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            results = self.reader.readtext(image)
            
            # Extract text and confidence scores
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter low confidence results
                    extracted_text.append(text)
            
            return '\n'.join(extracted_text)
        except Exception as e:
            print(f"EasyOCR failed: {e}")
            return ""
    def remove_watermark(self,img):
        """Load image in grayscale and apply adaptive threshold to remove watermark/grey text."""
        _, mask = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return mask
    def ocr_pdf(self, folder, output_file=None, preprocess=True):
        """
        Perform OCR on entire PDF
        """
        print(f"Converting PDF to images...")
        images = self.load_images_from_folder(folder)
        
        if not images:
            print("Failed to convert PDF to images")
            return ""
        
        all_text = []
        
        for i, image in enumerate(images):
            print(f"Processing page {i+1}/{len(images)}...")
            
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image
            
            # Perform OCR
            if self.use_easyocr:
                text = self.ocr_with_easyocr(processed_image)
            else:
                text = self.ocr_with_tesseract(processed_image)
            reshaped_text = arabic_reshaper.reshape(text)
            text = get_display(reshaped_text)
            if text.strip():
                all_text.append(f"--- Page {i+1} ---")
                all_text.append(text)
                all_text.append("")
        
        final_text = '\n'.join(all_text)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_text)
            print(f"OCR results saved to {output_file}")
        
        return final_text
    def clean_text(self,text: str) -> str:
        # Remove Unicode LTR/RTL marks (U+200E, U+200F, etc.)
        cleaned = re.sub(r'[\u200e\u200f]', '', text)
        return cleaned
    def compare_ocr_methods(self, folder, page_num=0):
        """Compare different OCR methods on a single page"""
        images = self.load_images_from_folder(folder)
        if not images or page_num >= len(images):
            return
        
        image = images[page_num]
        processed = self.preprocess_image(image)
        
        print(f"=== OCR Comparison for Page {page_num + 1} ===\n")
        
        # EasyOCR
        if hasattr(self, 'reader'):
            easy_text = self.ocr_with_easyocr(processed)
            print("EasyOCR Result:")
            print(easy_text)
            print("\n" + "="*50 + "\n")
            with open("output_file.txt", 'w', encoding='utf-8') as f:
                f.write(self.clean_text(easy_text))
        
        # Tesseract
        tesseract_text = self.ocr_with_tesseract(processed)
        print("Tesseract Result:")
        print(tesseract_text)
    
        print("\n" + "="*50 + "\n")
        with open("tesseract.txt", 'w', encoding='utf-8') as f:
                f.write(self.clean_text(tesseract_text))

# Usage examples
def main():
    # Initialize OCR with EasyOCR (generally better for Arabic)
    ocr = ArabicPDFOCR(use_easyocr=False)
    
    # Process your PDF
    folder = "COCArabe"
    
    try:
        # Extract text from entire PDF
        print("Starting OCR process...")
        # extracted_text = ocr.ocr_pdf(pdf_path, output_file="extracted_arabic.txt")
        
        # print("OCR completed!")
        # print("\nFirst 500 characters:")
        # print(extracted_text[:500])
        
        # # Compare OCR methods on first page
        # print("\n" + "="*60)
        # print("Comparing OCR methods on first page:")
        ocr.compare_ocr_methods(folder, page_num=16)
        
    except Exception as e:
        print(f"OCR failed: {e}")
        print("\nMake sure you have installed the required packages:")
        print("pip install opencv-python pillow pdf2image pytesseract easyocr PyMuPDF")
        print("\nFor Tesseract, also install:")
        print("- Windows: Download from GitHub releases")
        print("- Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-ara")
        print("- macOS: brew install tesseract")

if __name__ == "__main__":
    main()

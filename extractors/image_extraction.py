from PIL import Image
import pytesseract
import sys
from cleaner import cleaner
import cv2
import numpy as np

def preprocess(img_path):
    try:
        img = cv2.imread(img_path, 0)

        # upscale
        img = cv2.resize(img, None, fx=2, fy=2)

        # denoise
        img = cv2.medianBlur(img, 3)

        # threshold
        _, img = cv2.threshold(img, 0, 255,
                            cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    except Exception as e:
        print (f"Exception {e}")
        sys.exit(1)

    # deskew
    coords = np.column_stack(np.where(img > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    deskewed = cv2.warpAffine(img, M, (w, h),
                            flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_REPLICATE)

    return deskewed

def image_extractor(img_path):

    processed_img = preprocess(img_path)
    try:
        img = processed_img

        print("Running OCR (pytesseract.image_to_string):")
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
        print("=" * 60)
        print("OCR OUTPUT:")
        print("=" * 60)
        print(repr(text))
        print(f"\nLength: {len(text)} characters")
        print("=" * 60)
        
        if len(text.strip()) == 0:
            print("⚠️  Warning: OCR returned empty string. Image may not contain readable text.")
        else:
            print("✓ OCR extraction successful! Cleaned output: ")
            return cleaner(text)
            
    except FileNotFoundError as e:
        print(f"❌ FileNotFoundError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    return text

def main():
    import os
    file = os.path.abspath("/home/jyx1586/Calendar-Buddy/pdfs/Screenshot 2026-02-05 180738.png")
    image_extractor(file)

if __name__ == "__main__":
    main()
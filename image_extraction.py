from pathlib import Path
from PIL import Image
import pytesseract
import os, sys
from cleaner import cleaner

# Use path relative to this script
def image_extractor(file_name):
    BASE = Path(__file__).resolve().parent
    img_path = BASE / str(file_name)

    print("=" * 60)
    print("OCR Test: pytesseract image_to_string on 1.png")
    print("=" * 60)
    print(f"cwd:      {os.getcwd()}")
    print(f"script:   {Path(__file__).resolve()}")
    print(f"img_path: {img_path}")
    print(f"exists:   {img_path.exists()}")
    print()

    print()
    print("Opening image with PIL:")
    try:
        img = Image.open(img_path)
        print(f"  ✓ Image size: {img.size}")
        print(f"  ✓ Image mode: {img.mode}")
        print()

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

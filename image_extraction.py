from pathlib import Path
from PIL import Image
import pytesseract
import os, sys, shutil

# Use path relative to this script
BASE = Path(__file__).resolve().parent
img_path = BASE / "Photo_test" / "1.png"

print("=" * 60)
print("OCR Test: pytesseract image_to_string on 1.png")
print("=" * 60)
print(f"cwd:      {os.getcwd()}")
print(f"script:   {Path(__file__).resolve()}")
print(f"img_path: {img_path}")
print(f"exists:   {img_path.exists()}")
print()

# Check if Tesseract binary is available
tesseract_path = shutil.which('tesseract')
print(f"Tesseract binary found: {tesseract_path}")
if not tesseract_path:
    print("⚠️  WARNING: Tesseract OCR binary not found on PATH.")
    print("   Install with: brew install tesseract")
    print("   Or set pytesseract.pytesseract.tesseract_cmd manually.")
    print()

if not img_path.exists():
    print(f"❌ Error: image not found at {img_path}")
    sys.exit(1)

try:
    # If tesseract is in a non-standard location, set the path:
    pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"
    
    print("Checking Tesseract version:")
    try:
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract version: {version}")
    except Exception as e:
        print(f"  ✗ Tesseract error: {type(e).__name__}: {e}")
        print("    Tesseract binary is not installed or not on PATH.")
        print("    Install with: brew install tesseract")
        sys.exit(1)

    print()
    print("Opening image with PIL:")
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
        print("✓ OCR extraction successful!")
        
except FileNotFoundError as e:
    print(f"❌ FileNotFoundError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
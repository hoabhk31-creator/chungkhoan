#!/usr/bin/env python3
"""Download DejaVu fonts for PDF generation on Linux/Render.com"""
import os, urllib.request, sys

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

FONTS = {
    "arial.ttf":   "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.tar.bz2",
}

# Check if fonts already exist
reg = os.path.join(FONTS_DIR, "arial.ttf")
if os.path.exists(reg):
    print("Fonts already present, skipping download.")
    sys.exit(0)

# Use DejaVu fonts from system if available
linux_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
for p in linux_paths:
    if os.path.exists(p):
        base = os.path.dirname(p)
        import shutil
        # Map system fonts to expected names
        mapping = {
            "arial.ttf":   ("DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"),
            "arialbd.ttf": ("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"),
            "ariali.ttf":  ("DejaVuSans-Oblique.ttf", "LiberationSans-Italic.ttf", "FreeSansOblique.ttf"),
        }
        for dest_name, src_candidates in mapping.items():
            dest = os.path.join(FONTS_DIR, dest_name)
            for candidate in src_candidates:
                src = os.path.join(base, candidate)
                if os.path.exists(src):
                    shutil.copy2(src, dest)
                    print(f"Copied {src} -> {dest}")
                    break
        if os.path.exists(os.path.join(FONTS_DIR, "arial.ttf")):
            print("Fonts setup complete from system fonts.")
            sys.exit(0)
        break

print("System fonts not found. PDF will use built-in helvetica fallback.")

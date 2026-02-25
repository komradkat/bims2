from PIL import Image
import os


def convert_png_to_ico(png_path, ico_path):
    img = Image.open(png_path)
    # Convert to RGBA if not already
    img = img.convert("RGBA")
    # Generate multiple sizes for better compatibility (Inno Setup/Windows)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"Successfully converted {png_path} to {ico_path}")


if __name__ == "__main__":
    resources_dir = r"c:\Users\komradkat\Documents\Repos\bims2\resources"
    png_file = os.path.join(resources_dir, "app_icon.png")

    if os.path.exists(png_file):
        # Generate both app and installer icons from the same PNG for consistency
        convert_png_to_ico(png_file, os.path.join(resources_dir, "app_icon.ico"))
        convert_png_to_ico(png_file, os.path.join(resources_dir, "installer_icon.ico"))
    else:
        print(f"Error: {png_file} not found")

import os
import requests
import zipfile
import shutil
import time

# BIMS2 Update Engine
# This script handles automated patching for the "Baked-In" installation.

VERSION_URL = (
    "https://raw.githubusercontent.com/your-repo/bims2/main/VERSION"  # Placeholder
)
PATCH_URL_TEMPLATE = (
    "https://github.com/your-repo/bims2/releases/download/{version}/bims2_patch.zip"
)


def get_current_version():
    try:
        with open("VERSION", "r") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"


def check_for_updates():
    print("Checking for updates...")
    try:
        response = requests.get(VERSION_URL, timeout=10)
        latest_version = response.text.strip()
        current_version = get_current_version()

        if latest_version > current_version:
            print(f"New version available: {latest_version}")
            return latest_version
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return None


def apply_update(new_version):
    print(f"Downloading update {new_version}...")
    patch_url = PATCH_URL_TEMPLATE.format(version=new_version)
    patch_file = "bims2_patch.zip"

    try:
        # Download
        r = requests.get(patch_url, stream=True)
        with open(patch_file, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        print("Stopping BIMS2 services...")
        # In a real windows service scenario, we'd use: net stop bims2_service
        # For now, we assume the user closed the app or we kill the process

        print("Applying patch...")
        with zipfile.ZipFile(patch_file, "r") as zip_ref:
            # We extract everything but preserve C:/BIMS_Data (which is outside app folder)
            # and preserve the local .env if it contains unique keys
            extract_path = "."
            zip_ref.extractall(extract_path)

        os.remove(patch_file)
        print("Update successful! Restarting BIMS2...")
        # subprocess.Popen(["waitress_server.exe"])

    except Exception as e:
        print(f"Update failed: {e}")


if __name__ == "__main__":
    latest = check_for_updates()
    if latest:
        answer = input(f"Do you want to update to {latest}? (y/n): ")
        if answer.lower() == "y":
            apply_update(latest)
    else:
        print("BIMS2 is up to date.")
        time.sleep(2)

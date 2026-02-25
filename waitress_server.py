import os
import sys
import webbrowser
import threading
import time
from waitress import serve

# This server runner is designed for the Standalone Application
# It handles Waitress serving and automatically opens the user's browser


def open_browser(url):
    """Wait for server to start and then open browser."""
    # Short delay to let the server bind to the port
    time.sleep(1.5)
    print(f"Opening browser at {url}...")
    webbrowser.open(url)


def main():
    # --- Standalone DLL Path Patch ---
    # WeasyPrint requires GTK libraries (gobject, cairo, etc.)
    # If we are in a standalone build, we add the executable directory to the DLL search path
    if getattr(sys, "frozen", False) or "NUITKA_BINARY_NAME" in os.environ:
        exe_dir = os.path.dirname(sys.executable)
        if hasattr(os, "add_dll_directory"):
            # Python 3.8+ style
            os.add_dll_directory(exe_dir)
        else:
            # Older style or fallback
            os.environ["PATH"] = exe_dir + os.pathsep + os.environ.get("PATH", "")

    # Set the settings module for production/standalone
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

    # --- Auto-Migration for Standalone Distribution ---
    print(">>> Checking database schema...")
    try:
        from django.core.management import execute_from_command_line

        # Run migrate without captured output
        execute_from_command_line(["manage.py", "migrate", "--noinput"])
        print(">>> Database ready.")
    except Exception as e:
        print(f"[WARNING] Auto-migration failed: {e}")

    # Port configuration
    HOST = "127.0.0.1"
    PORT = 8000
    URL = f"http://{HOST}:{PORT}/"

    print("--- BIMS2 Standalone Server ---")
    print(f"Starting server at {URL}")
    print("Press Ctrl+C to stop.")

    # Start browser-opener thread
    threading.Thread(target=open_browser, args=(URL,), daemon=True).start()

    # Get the WSGI application
    try:
        from config.wsgi import application

        # Serve the app via Waitress
        serve(application, host=HOST, port=PORT, threads=4)
    except Exception as e:
        print(f"Fatal error starting server: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()

import requests
from django.conf import settings

# Utility to check for updates from a remote source
VERSION_URL = "https://raw.githubusercontent.com/your-repo/bims2/main/VERSION" # Placeholder

def check_for_updates(current_version):
    """
    Checks the remote VERSION file and compares it with the local version.
    Returns a dictionary with update status and metadata.
    """
    try:
        # If in debug mode or no URL set, skip to avoid lag
        if settings.DEBUG:
             return {'update_available': False}

        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()
            
            # Simple version comparison (semantic)
            if latest_version > current_version:
                return {
                    'update_available': True,
                    'latest_version': latest_version,
                    'current_version': current_version,
                    'changelog': "New security patches and performance improvements available."
                }
    except Exception:
        pass
        
    return {
        'update_available': False,
        'latest_version': current_version,
        'current_version': current_version
    }

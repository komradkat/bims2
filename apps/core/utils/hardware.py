"""
Hardware ID generation utility for license binding.
Generates a unique identifier based on system hardware characteristics.
"""

import hashlib
import platform
import uuid
import subprocess
import os


def get_drive_serial():
    """
    Get the Volume Serial Number of the drive where the script is currently running.
    Useful for portable apps tied to a USB/Disk.
    """
    try:
        # Get the drive letter (e.g., 'C:')
        drive = os.path.splitdrive(os.path.abspath(__file__))[0]
        if not drive:
            return None

        # Run wmic to get the volume serial
        cmd = f'wmic logicaldisk where name="{drive}" get volumeserialnumber'
        output = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode()

        # Parse output (typically: VolumeSerialNumber \n XXXXXXXX)
        lines = [line.strip() for line in output.split("\n") if line.strip()]
        if len(lines) > 1:
            return lines[1]
    except Exception:
        return None
    return None


def get_hardware_id():
    """
    Generate unique hardware identifier based on system info.

    This creates a consistent hash based on:
    - MAC address (network interface)
    - Platform system name
    - Node name (hostname)

    Returns:
        str: SHA-256 hash of hardware characteristics
    """
    # Get MAC address
    mac = ":".join(
        [
            "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
            for elements in range(0, 2 * 6, 2)
        ][::-1]
    )

    # Get platform info
    system_info = f"{platform.system()}-{platform.node()}-{mac}"

    # Create hash
    hardware_id = hashlib.sha256(system_info.encode()).hexdigest()

    return hardware_id

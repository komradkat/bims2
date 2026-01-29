"""
Hardware ID generation utility for license binding.
Generates a unique identifier based on system hardware characteristics.
"""

import hashlib
import platform
import uuid


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
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                    for elements in range(0, 2*6, 2)][::-1])
    
    # Get platform info
    system_info = f"{platform.system()}-{platform.node()}-{mac}"
    
    # Create hash
    hardware_id = hashlib.sha256(system_info.encode()).hexdigest()
    
    return hardware_id

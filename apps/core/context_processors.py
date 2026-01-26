# Context processors for global template variables

def barangay_info(request):
    """Provide barangay information to all templates"""
    return {
        'barangay_info': {
            'name': 'Barangay 53',
            'full_name': 'Barangay 53, Caloocan City',
            'logo_url': None,  # TODO: Add logo path when available
        }
    }


def user_info(request):
    """Provide user information to all templates (placeholder for now)"""
    return {
        'user_info': {
            'name': 'Admin User',
            'role': 'Administrator',
            'position': 'Barangay Secretary',
        }
    }


def tier_info(request):
    """Provide tier/license information to all templates"""
    # For development, set to Ultra to show all features
    return {
        'tier_info': {
            'name': 'Ultra',
            'level': 3,  # 1=Community, 2=Pro, 3=Ultra
            'badge_color': 'secondary',  # DaisyUI color
            'features': {
                'residents': True,
                'certificates': True,
                'business': True,
                'blotter': True,
                'finance': True,
                'audit_logs': True,
                'gis_map': True,
            }
        }
    }

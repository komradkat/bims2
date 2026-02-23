# Context processors for global template variables

def barangay_info(request):
    """Provide barangay information to all templates"""
    from apps.core.models import BarangayInfo
    
    info = BarangayInfo.objects.first()
    
    if info:
        data = {
            'name': info.name,
            'full_name': f"{info.name}, {info.full_address}",
            'logo_url': info.logo.url if info.logo else None,
            'address': info.full_address,
            'street': info.street,
            'city': info.city_municipality,
            'province': info.province,
            'region': info.region,
            'zip_code': info.zip_code,
            'contact': info.contact_number,
            'email': info.email,
        }
    else:
        # Fallback for initial setup
        data = {
            'name': 'BIMS Setup',
            'full_name': 'Barangay Information Management System',
            'logo_url': None,
        }
        
    return {'barangay_info': data}


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
    # Get license data from middleware (attached to request)
    license_data = getattr(request, 'license', None)
    from apps.core.utils.hardware import get_hardware_id
    hardware_id = get_hardware_id()
    
    if not license_data:
        # Fallback to Community if middleware hasn't run yet
        tier = 'community'
    else:
        tier = license_data.get('tier', 'community')
    
    # Map tier to level and features
    tier_config = {
        'community': {
            'name': 'Community',
            'level': 1,
            'badge_color': 'neutral',
            'features': {
                'residents': True,
                'certificates': True,
                'business': False,
                'blotter': True,
                'finance': False,
                'audit_logs': False,
                'gis_map': False,
            }
        },
        'pro': {
            'name': 'Pro',
            'level': 2,
            'badge_color': 'primary',
            'features': {
                'residents': True,
                'certificates': True,
                'business': True,
                'blotter': True,
                'finance': True,
                'audit_logs': True,
                'gis_map': False,
            }
        },
        'ultra': {
            'name': 'Ultra',
            'level': 3,
            'badge_color': 'secondary',
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
    
    config = tier_config.get(tier, tier_config['community'])
    
    # Add license-specific info if available
    if license_data:
        config['expiry_date'] = license_data.get('expiry_date')
        config['max_users'] = license_data.get('max_users', 5)
        config['key_preview'] = license_data.get('key_preview', 'Community (Free)')
    
    config['hardware_id'] = hardware_id
    
    return {'tier_info': config}

def notifications(request):
    """Provide recent notifications to the topbar"""
    if not request.user.is_authenticated:
        return {}
    
    from apps.core.models import Notification
    
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return {
        'unread_notifications_count': unread_count,
        'recent_notifications': recent_notifications,
    }

def system_version(request):
    """Provide system version information to all templates"""
    from django.conf import settings
    return {
        'system_version': getattr(settings, 'BIMS_VERSION', '1.0.0-dev')
    }

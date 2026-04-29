# Context processors for global template variables


def barangay_info(request):
    """Provide barangay information to all templates"""
    from apps.core.models import BarangayInfo

    info = BarangayInfo.objects.first()

    if info:
        data = {
            "name": info.name,
            "full_name": f"{info.name}, {info.full_address}",
            "logo_url": info.logo_url,
            "address": info.full_address,
            "street": info.street,
            "city": info.city_municipality,
            "province": info.province,
            "region": info.region,
            "zip_code": info.zip_code,
            "contact": info.contact_number,
            "email": info.email,
        }
    else:
        # Fallback for initial setup
        data = {
            "name": "BIMS Setup",
            "full_name": "Barangay Information Management System",
            "logo_url": None,
        }

    return {"barangay_info": data}


def user_info(request):
    """Provide user information to all templates (placeholder for now)"""
    return {
        "user_info": {
            "name": "Admin User",
            "role": "Administrator",
            "position": "Barangay Secretary",
        }
    }


def tier_info(request):
    """Provide static tier/license information for the Community Edition"""
    return {
        "tier_info": {
            "name": "Community Edition",
            "level": 1,
            "badge_color": "neutral",
            "features": {
                "residents": True,
                "certificates": True,
                "business": True,  # Enabled for CE
                "blotter": True,
                "finance": True,  # Enabled for CE
                "audit_logs": True,  # Enabled for CE
                "gis_map": True,  # Enabled for CE
            },
            "expiry_date": None,
            "max_users": 999,
            "key_preview": "Community Edition",
            "hardware_id": "COMMUNITY-EDITION",
        }
    }


def notifications(request):
    """Provide recent notifications to the topbar"""
    if not request.user.is_authenticated:
        return {}

    from apps.core.models import Notification

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent_notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:5]

    return {
        "unread_notifications_count": unread_count,
        "recent_notifications": recent_notifications,
    }


def system_version(request):
    """Provide system version information to all templates"""
    from django.conf import settings

    return {"system_version": getattr(settings, "BIMS_VERSION", "1.0.0-dev")}

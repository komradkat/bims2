import logging
from .models import SystemLog

logger = logging.getLogger("apps")


def log_system_event(action, user=None, details=None, request=None):
    """
    Helper function to log significant system events.
    """
    if details is None:
        details = {}

    ip_address = None
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        if user is None and request.user.is_authenticated:
            user = request.user

    try:
        log_entry = SystemLog.objects.create(
            user=user, action=action, details=details, ip_address=ip_address
        )

        # Also log to our rotating file for persistence/diagnostics
        log_msg = f"SYSTEM_EVENT: {action} | User: {user} | Details: {details} | IP: {ip_address}"
        if action == "CRITICAL_ERROR":
            logger.error(log_msg)
        else:
            logger.info(log_msg)

        return log_entry
    except Exception as e:
        # Fallback to file logging if DB write fails
        logger.error(
            f"Failed to create SystemLog entry: {e}. Original event: {action} {details}"
        )
        return None

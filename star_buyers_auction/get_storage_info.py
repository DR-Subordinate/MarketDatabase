import shutil
from django.conf import settings

def get_disk_usage():
    """
    Get storage information for the media directory.
    Returns a dictionary containing total, free, and used space in GB,
    along with usage percentage.
    """
    media_root = settings.MEDIA_ROOT

    total, used, free = shutil.disk_usage(media_root)

    # Convert to GB for readability
    total_gb = total / (2**30)
    free_gb = free / (2**30)
    used_gb = used / (2**30)

    return {
        'total_gb': round(total_gb, 2),
        'free_gb': round(free_gb, 2),
        'used_gb': round(used_gb, 2),
        'usage_percent': round((used / total) * 100, 2)
    }

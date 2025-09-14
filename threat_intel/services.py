from .models import Indicator
from .tasks import task_get_domain_intel, task_get_hash_intel, task_get_ip_intel


def get_domain_intel(domain: str) -> Indicator:
    """
    Triggers an asynchronous task to retrieve intelligence for a given domain.
    """
    indicator, _ = Indicator.objects.get_or_create(
        value=domain, defaults={"type": Indicator.IndicatorType.DOMAIN}
    )
    task_get_domain_intel.delay(domain)
    return indicator


def get_ip_intel(ip_address: str) -> Indicator:
    """
    Triggers an asynchronous task to retrieve intelligence for a given IP address.
    """
    indicator, _ = Indicator.objects.get_or_create(
        value=ip_address, defaults={"type": Indicator.IndicatorType.IPV4}
    )
    task_get_ip_intel.delay(ip_address)
    return indicator


def get_hash_intel(file_hash: str) -> Indicator:
    """
    Triggers an asynchronous task to retrieve intelligence for a given file hash.
    """
    # Basic type inference
    if len(file_hash) == 32:
        hash_type = Indicator.IndicatorType.MD5
    elif len(file_hash) == 40:
        hash_type = Indicator.IndicatorType.SHA1
    else:
        hash_type = Indicator.IndicatorType.SHA256

    indicator, _ = Indicator.objects.get_or_create(
        value=file_hash, defaults={"type": hash_type}
    )
    task_get_hash_intel.delay(file_hash)
    return indicator

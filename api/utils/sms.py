import os
import logging

logger = logging.getLogger(__name__)


def send_sms(phone: str, text: str) -> bool:
    """Placeholder SMS sender. Replace backend with Tello or other provider.

    phone should be in local format (9 digits) e.g. 923123456
    """
    # Example: log and return True to simulate sending
    logger.info('Sending SMS to %s: %s', phone, text)
    # TODO: implement HTTP request to SMS provider using API key from env
    return True

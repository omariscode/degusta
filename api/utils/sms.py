import os
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def send_sms(phone: list, text: str) -> bool:

    try:    
        message = client.messages.create(
            body=text,
            from_='+18777804236',  
            to=phone
        )
        logger.info(f"SMS sent to {phone}: {message.account_sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone}: {e}")
        return False
    
    return True
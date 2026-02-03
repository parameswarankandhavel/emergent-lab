"""Pluggable SMS OTP service for mobile verification.

This module provides a structure for SMS OTP delivery.
Currently returns mock success for design purposes.

To integrate a real SMS provider (Twilio, AWS SNS, etc.):
1. Install provider SDK (e.g., pip install twilio)
2. Add provider credentials to .env
3. Implement actual send logic in send_mobile_otp()
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def send_mobile_otp(phone_number: str, otp_code: str) -> Tuple[bool, str]:
    """
    Send OTP via SMS to mobile number.
    
    Args:
        phone_number: Recipient phone number (E.164 format recommended)
        otp_code: 6-digit OTP code to send
    
    Returns:
        Tuple[bool, str]: (success, message)
    
    IMPLEMENTATION GUIDE:
    --------------------
    
    For Twilio:
    -----------
    from twilio.rest import Client
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"Your Burnout Checker verification code is: {otp_code}. Valid for 10 minutes.",
        from_='+1234567890',
        to=phone_number
    )
    return True, "SMS sent successfully"
    
    For AWS SNS:
    -----------
    import boto3
    sns = boto3.client('sns')
    response = sns.publish(
        PhoneNumber=phone_number,
        Message=f"Your Burnout Checker verification code is: {otp_code}. Valid for 10 minutes."
    )
    return True, "SMS sent successfully"
    """
    
    # MOCK IMPLEMENTATION - Remove in production
    logger.warning(f"MOCK SMS: Would send OTP {otp_code} to {phone_number}")
    logger.info("SMS provider not configured. Using mock success response.")
    
    # Return mock success
    return True, "SMS sent successfully (mock mode)"
    
    # PRODUCTION: Replace above with actual provider implementation
    # Uncomment and implement based on your chosen provider
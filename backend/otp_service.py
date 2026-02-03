import random
import string
from datetime import datetime, timedelta
from database import store_otp, get_otp, increment_resend_count
from config import settings
import logging

logger = logging.getLogger(__name__)

def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=6))

def create_otp(session_id: str, otp_type: str, target: str) -> tuple[str, bool, str]:
    """Create OTP and return (otp_code, success, message)"""
    # Check resend limit
    existing_otp = get_otp(session_id, otp_type)
    if existing_otp:
        resend_count = existing_otp.get("resend_count", 0)
        if resend_count >= settings.otp_max_resend_attempts:
            return "", False, f"Maximum resend limit ({settings.otp_max_resend_attempts}) reached. Please try again later."
    
    # Generate new OTP
    otp_code = generate_otp_code()
    
    # Store in database
    try:
        store_otp(session_id, otp_type, otp_code, target)
        
        # Increment resend count if not first attempt
        if existing_otp:
            increment_resend_count(session_id, otp_type)
        
        logger.info(f"OTP created for session {session_id}, type {otp_type}")
        return otp_code, True, "OTP created successfully"
    except Exception as e:
        logger.error(f"Error creating OTP: {e}")
        return "", False, "Failed to create OTP. Please try again."
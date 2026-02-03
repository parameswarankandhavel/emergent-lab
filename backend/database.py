from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
from config import settings
import logging

logger = logging.getLogger(__name__)

# MongoDB client
client = MongoClient(settings.mongo_url)
db = client.burnout_checker

# Collections
sessions_collection = db.sessions
assessments_collection = db.assessments
reports_collection = db.reports
otp_collection = db.otps

# Create indexes for automatic cleanup and fast lookups
def init_db():
    """Initialize database indexes"""
    try:
        # Sessions: TTL index for auto-cleanup after 24 hours
        sessions_collection.create_index(
            "created_at",
            expireAfterSeconds=settings.session_expiry_hours * 3600
        )
        sessions_collection.create_index("session_id", unique=True)
        
        # OTPs: TTL index for auto-cleanup
        otp_collection.create_index(
            "created_at",
            expireAfterSeconds=settings.otp_expiry_minutes * 60
        )
        otp_collection.create_index([("session_id", ASCENDING), ("type", ASCENDING)])
        
        # Assessments
        assessments_collection.create_index("session_id")
        
        # Reports
        reports_collection.create_index("session_id", unique=True)
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# Session management
def create_session(session_id: str, data: dict):
    """Create a new session"""
    session_data = {
        "session_id": session_id,
        "data": data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    sessions_collection.insert_one(session_data)
    return session_data

def get_session(session_id: str):
    """Get session by ID"""
    return sessions_collection.find_one({"session_id": session_id})

def update_session(session_id: str, data: dict):
    """Update session data"""
    sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "data": data,
                "updated_at": datetime.utcnow()
            }
        }
    )

def delete_session(session_id: str):
    """Delete a session"""
    sessions_collection.delete_one({"session_id": session_id})

# OTP management
def store_otp(session_id: str, otp_type: str, otp_code: str, target: str):
    """Store OTP with expiry"""
    otp_data = {
        "session_id": session_id,
        "type": otp_type,  # 'email' or 'mobile'
        "code": otp_code,
        "target": target,  # email address or phone number
        "verified": False,
        "attempts": 0,
        "resend_count": 0,
        "created_at": datetime.utcnow()
    }
    otp_collection.insert_one(otp_data)
    return otp_data

def get_otp(session_id: str, otp_type: str):
    """Get the latest OTP for a session and type"""
    return otp_collection.find_one(
        {"session_id": session_id, "type": otp_type},
        sort=[("created_at", -1)]
    )

def verify_otp(session_id: str, otp_type: str, otp_code: str) -> tuple[bool, str]:
    """Verify OTP and return (success, message)"""
    otp_record = get_otp(session_id, otp_type)
    
    if not otp_record:
        return False, "OTP not found. Please request a new one."
    
    # Check if already verified
    if otp_record.get("verified"):
        return False, "OTP already used. Please request a new one."
    
    # Check expiry
    expiry_time = otp_record["created_at"] + timedelta(minutes=settings.otp_expiry_minutes)
    if datetime.utcnow() > expiry_time:
        return False, "OTP expired. Please request a new one."
    
    # Check attempts
    if otp_record.get("attempts", 0) >= 5:
        return False, "Too many failed attempts. Please request a new one."
    
    # Verify code
    if otp_record["code"] == otp_code:
        otp_collection.update_one(
            {"_id": otp_record["_id"]},
            {"$set": {"verified": True}}
        )
        return True, "OTP verified successfully"
    else:
        otp_collection.update_one(
            {"_id": otp_record["_id"]},
            {"$inc": {"attempts": 1}}
        )
        return False, "Invalid OTP. Please try again."

def increment_resend_count(session_id: str, otp_type: str) -> int:
    """Increment and return resend count"""
    otp_record = get_otp(session_id, otp_type)
    if otp_record:
        new_count = otp_record.get("resend_count", 0) + 1
        otp_collection.update_one(
            {"_id": otp_record["_id"]},
            {"$set": {"resend_count": new_count}}
        )
        return new_count
    return 0

def check_otp_verified(session_id: str, otp_type: str) -> bool:
    """Check if OTP is verified"""
    otp_record = get_otp(session_id, otp_type)
    return otp_record and otp_record.get("verified", False)

# Assessment management
def store_assessment(session_id: str, answers: dict, score: int, level: str):
    """Store assessment results"""
    assessment_data = {
        "session_id": session_id,
        "answers": answers,
        "score": score,
        "level": level,
        "created_at": datetime.utcnow()
    }
    assessments_collection.insert_one(assessment_data)
    return assessment_data

def get_assessment(session_id: str):
    """Get assessment by session ID"""
    return assessments_collection.find_one({"session_id": session_id})

# Report management
def store_report(session_id: str, report_content: str, user_data: dict):
    """Store generated report"""
    report_data = {
        "session_id": session_id,
        "report_content": report_content,
        "user_data": user_data,
        "created_at": datetime.utcnow(),
        "email_sent": False
    }
    reports_collection.insert_one(report_data)
    return report_data

def get_report(session_id: str):
    """Get report by session ID"""
    return reports_collection.find_one({"session_id": session_id})

def mark_report_email_sent(session_id: str):
    """Mark report as email sent"""
    reports_collection.update_one(
        {"session_id": session_id},
        {"$set": {"email_sent": True, "email_sent_at": datetime.utcnow()}}
    )
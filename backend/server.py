from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
import uuid
import logging
from datetime import datetime

# Import services
from database import (
    init_db, create_session, get_session, update_session,
    store_assessment, get_assessment, store_report, get_report,
    check_otp_verified, verify_otp, mark_report_email_sent
)
from otp_service import create_otp
from email_service import send_otp_email, send_report_email
from sms_service import send_mobile_otp
from ai_service import generate_burnout_report, validate_report_content
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Burnout Score Checker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

# Pydantic models for request/response
class UserRegistration(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=15)

class OTPRequest(BaseModel):
    session_id: str
    otp_type: str  # 'email' or 'mobile'

class OTPVerification(BaseModel):
    session_id: str
    otp_type: str
    otp_code: str

class AssessmentSubmission(BaseModel):
    session_id: str
    answers: Dict[int, int]  # question_id -> answer_value (0-3)

class PaymentReturn(BaseModel):
    session_id: str

# Helper function to calculate burnout score
def calculate_burnout_score(answers: Dict[int, int]) -> tuple[int, str, str]:
    """Calculate burnout score and determine level"""
    raw_score = sum(answers.values())
    score = round((raw_score / 21) * 100)
    
    if score <= 33:
        level = "Low"
        preview = "You're managing well! Your burnout risk is low."
    elif score <= 66:
        level = "Moderate"
        preview = "You're showing signs of moderate burnout."
    else:
        level = "High"
        preview = "Your burnout risk is high. It's important to take action now."
    
    return score, level, preview

# Answer label mapping
ANSWER_LABELS = {
    1: ["Never", "Sometimes", "Often", "Always"],
    2: ["Never", "Sometimes", "Often", "Always"],
    3: ["High and energized", "Moderate", "Low", "Very low or none"],
    4: ["Never", "Sometimes", "Often", "Always"],
    5: ["Very satisfied", "Somewhat satisfied", "Not very satisfied", "Not satisfied at all"],
    6: ["Excellent", "Good", "Poor", "Very poor"],
    7: ["Always", "Often", "Sometimes", "Never"]
}

def get_answer_text(question_id: int, answer_value: int) -> str:
    """Convert answer value to text label"""
    return ANSWER_LABELS.get(question_id, [])[answer_value] if answer_value < len(ANSWER_LABELS.get(question_id, [])) else "Unknown"

# API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/register")
async def register_user(registration: UserRegistration):
    """
    Step 1: Register user and create session
    Returns session_id for subsequent requests
    """
    try:
        # Create unique session ID
        session_id = str(uuid.uuid4())
        
        # Store user data in session
        session_data = {
            "full_name": registration.full_name,
            "email": registration.email,
            "mobile": registration.mobile,
            "email_verified": False,
            "mobile_verified": False,
            "assessment_completed": False,
            "payment_completed": False,
            "report_generated": False,
            "step": "registration"
        }
        
        create_session(session_id, session_data)
        
        logger.info(f"User registered: {registration.email}, session: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Registration successful. Please verify your email.",
            "next_step": "email_verification"
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/otp/send")
async def send_otp(request: OTPRequest):
    """
    Step 2 & 3: Send OTP for email or mobile verification
    """
    try:
        # Get session
        session = get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        # Determine target (email or mobile)
        if request.otp_type == "email":
            target = session_data["email"]
            user_name = session_data["full_name"]
        elif request.otp_type == "mobile":
            target = session_data["mobile"]
            user_name = session_data["full_name"]
        else:
            raise HTTPException(status_code=400, detail="Invalid OTP type")
        
        # Create OTP
        otp_code, success, message = create_otp(request.session_id, request.otp_type, target)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Send OTP
        if request.otp_type == "email":
            send_success, send_message = send_otp_email(target, otp_code, user_name)
        else:  # mobile
            send_success, send_message = send_mobile_otp(target, otp_code)
        
        if not send_success:
            raise HTTPException(status_code=500, detail=send_message)
        
        logger.info(f"OTP sent to {target} ({request.otp_type})")
        
        return {
            "success": True,
            "message": f"OTP sent to your {request.otp_type}",
            "expires_in_minutes": settings.otp_expiry_minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send OTP error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@app.post("/api/otp/verify")
async def verify_otp_endpoint(verification: OTPVerification):
    """
    Step 2 & 3: Verify OTP for email or mobile
    """
    try:
        # Get session
        session = get_session(verification.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify OTP
        success, message = verify_otp(verification.session_id, verification.otp_type, verification.otp_code)
        
        if not success:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": message}
            )
        
        # Update session
        session_data = session["data"]
        if verification.otp_type == "email":
            session_data["email_verified"] = True
            next_step = "mobile_verification"
        else:
            session_data["mobile_verified"] = True
            next_step = "assessment"
        
        session_data["step"] = next_step
        update_session(verification.session_id, session_data)
        
        logger.info(f"OTP verified for session {verification.session_id} ({verification.otp_type})")
        
        return {
            "success": True,
            "message": "Verification successful",
            "next_step": next_step
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify OTP error: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

@app.post("/api/assessment/submit")
async def submit_assessment(submission: AssessmentSubmission):
    """
    Step 4: Submit assessment and get preview results
    Requires email AND mobile verification
    """
    try:
        # Get session
        session = get_session(submission.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        # Check verification status
        if not session_data.get("email_verified"):
            raise HTTPException(status_code=403, detail="Email not verified")
        
        if not session_data.get("mobile_verified"):
            raise HTTPException(status_code=403, detail="Mobile not verified")
        
        # Validate answers
        if len(submission.answers) != 7:
            raise HTTPException(status_code=400, detail="All 7 questions must be answered")
        
        # Calculate score
        score, level, preview = calculate_burnout_score(submission.answers)
        
        # Convert answer values to text labels
        answer_texts = {
            q_id: get_answer_text(q_id, ans_val)
            for q_id, ans_val in submission.answers.items()
        }
        
        # Store assessment
        store_assessment(submission.session_id, answer_texts, score, level)
        
        # Update session
        session_data["assessment_completed"] = True
        session_data["score"] = score
        session_data["level"] = level
        session_data["answers"] = answer_texts
        session_data["step"] = "payment"
        update_session(submission.session_id, session_data)
        
        logger.info(f"Assessment submitted for session {submission.session_id}, score: {score}")
        
        return {
            "success": True,
            "score": score,
            "level": level,
            "preview_insight": preview,
            "next_step": "payment",
            "message": "Assessment complete. Unlock your full report to continue."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit assessment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit assessment")

@app.get("/api/payment/redirect")
async def get_payment_redirect(session_id: str):
    """
    Step 5: Get Gumroad payment URL with return parameters
    """
    try:
        # Get session
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        # Check if assessment is completed
        if not session_data.get("assessment_completed"):
            raise HTTPException(status_code=403, detail="Assessment not completed")
        
        # Build Gumroad URL with return parameter
        return_url = f"{settings.app_base_url}/payment-return?session_id={session_id}"
        gumroad_url = f"{settings.gumroad_product_url}?wanted=true&return_url={return_url}"
        
        logger.info(f"Payment redirect requested for session {session_id}")
        
        return {
            "success": True,
            "payment_url": gumroad_url,
            "message": "Redirect to Gumroad for payment"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment redirect error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment redirect")

@app.post("/api/payment/confirm")
async def confirm_payment(payment: PaymentReturn):
    """
    Step 6: Confirm payment and trigger report generation
    Called after user returns from Gumroad with ?payment=success
    """
    try:
        # Get session
        session = get_session(payment.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        # Check if assessment is completed
        if not session_data.get("assessment_completed"):
            raise HTTPException(status_code=403, detail="Assessment not completed")
        
        # Check if payment already processed
        if session_data.get("payment_completed"):
            # Report already exists
            existing_report = get_report(payment.session_id)
            if existing_report:
                return {
                    "success": True,
                    "message": "Payment already processed",
                    "report_content": existing_report["report_content"]
                }
        
        # Mark payment as completed
        session_data["payment_completed"] = True
        session_data["step"] = "report_generation"
        update_session(payment.session_id, session_data)
        
        logger.info(f"Payment confirmed for session {payment.session_id}")
        
        return {
            "success": True,
            "message": "Payment confirmed. Generating your report...",
            "next_step": "report_generation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm payment")

@app.post("/api/report/generate")
async def generate_report(request: PaymentReturn):
    """
    Step 7: Generate AI report (only after payment confirmation)
    This endpoint should only be called ONCE per session
    """
    try:
        # Get session
        session = get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        # CRITICAL: Payment gate - must have paid
        if not session_data.get("payment_completed"):
            raise HTTPException(status_code=403, detail="Payment required")
        
        # Check if report already generated (prevent duplicates)
        existing_report = get_report(request.session_id)
        if existing_report:
            logger.warning(f"Report already exists for session {request.session_id}")
            return {
                "success": True,
                "message": "Report already generated",
                "report_content": existing_report["report_content"],
                "already_existed": True
            }
        
        # Get assessment data
        assessment = get_assessment(request.session_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Generate AI report (SINGLE CALL)
        success, report_content, error = generate_burnout_report(
            user_full_name=session_data["full_name"],
            burnout_score=session_data["score"],
            burnout_level=session_data["level"],
            answers=session_data["answers"]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=error)
        
        # Validate report quality
        if not validate_report_content(report_content):
            logger.error("Generated report failed quality validation")
            raise HTTPException(status_code=500, detail="Report generation failed quality check")
        
        # Store report in database
        user_data = {
            "full_name": session_data["full_name"],
            "email": session_data["email"],
            "mobile": session_data["mobile"]
        }
        store_report(request.session_id, report_content, user_data)
        
        # Update session
        session_data["report_generated"] = True
        session_data["step"] = "report_delivery"
        update_session(request.session_id, session_data)
        
        logger.info(f"Report generated successfully for session {request.session_id}")
        
        return {
            "success": True,
            "message": "Report generated successfully",
            "report_content": report_content,
            "next_step": "email_delivery"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@app.post("/api/report/email")
async def email_report(request: PaymentReturn):
    """
    Step 8: Email the report to user
    """
    try:
        # Get session
        session = get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        # Check payment and report generation
        if not session_data.get("payment_completed"):
            raise HTTPException(status_code=403, detail="Payment required")
        
        if not session_data.get("report_generated"):
            raise HTTPException(status_code=403, detail="Report not generated")
        
        # Get report
        report = get_report(request.session_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check if email already sent
        if report.get("email_sent"):
            return {
                "success": True,
                "message": "Report already sent to your email",
                "already_sent": True
            }
        
        # Send email
        success, message = send_report_email(
            email=session_data["email"],
            user_name=session_data["full_name"],
            report_content=report["report_content"]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        # Mark as sent
        mark_report_email_sent(request.session_id)
        
        logger.info(f"Report emailed to {session_data['email']}")
        
        return {
            "success": True,
            "message": "Report sent to your email successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email report error: {e}")
        raise HTTPException(status_code=500, detail="Failed to email report")

@app.get("/api/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status and progress"""
    try:
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session["data"]
        
        return {
            "success": True,
            "session_id": session_id,
            "current_step": session_data.get("step", "unknown"),
            "email_verified": session_data.get("email_verified", False),
            "mobile_verified": session_data.get("mobile_verified", False),
            "assessment_completed": session_data.get("assessment_completed", False),
            "payment_completed": session_data.get("payment_completed", False),
            "report_generated": session_data.get("report_generated", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

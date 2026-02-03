import resend
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Resend with API key
resend.api_key = settings.resend_api_key

def send_otp_email(email: str, otp_code: str, user_name: str = "User") -> tuple[bool, str]:
    """Send OTP via email using Resend"""
    try:
        params = {
            "from": settings.from_email,
            "to": [email],
            "subject": "Your Burnout Score Checker Verification Code",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .otp-box {{ background-color: white; border: 2px solid #2563eb; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #6b7280; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Burnout Score Checker</h1>
                    </div>
                    <div class="content">
                        <p>Hello {user_name},</p>
                        <p>Your verification code for the Burnout Score Checker is:</p>
                        <div class="otp-box">
                            <div class="otp-code">{otp_code}</div>
                        </div>
                        <p><strong>This code will expire in {settings.otp_expiry_minutes} minutes.</strong></p>
                        <p>If you didn't request this code, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        response = resend.Emails.send(params)
        logger.info(f"OTP email sent successfully to {email}")
        return True, "OTP sent successfully"
        
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")
        return False, f"Failed to send OTP email: {str(e)}"

def send_report_email(email: str, user_name: str, report_content: str) -> tuple[bool, str]:
    """Send full burnout report via email using Resend"""
    try:
        params = {
            "from": settings.from_email,
            "to": [email],
            "subject": "Your Personalized Burnout Recovery Report",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff; }}
                    .header {{ background-color: #2563eb; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 40px; background-color: #f9fafb; }}
                    .report {{ background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    h2 {{ color: #1f2937; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
                    h3 {{ color: #374151; margin-top: 25px; }}
                    ul {{ margin-left: 20px; }}
                    li {{ margin-bottom: 10px; }}
                    .footer {{ text-align: center; margin-top: 30px; padding: 20px; font-size: 12px; color: #6b7280; }}
                    strong {{ color: #1f2937; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌟 Your Personalized Burnout Recovery Report</h1>
                    </div>
                    <div class="content">
                        <p style="font-size: 16px;">Dear {user_name},</p>
                        <p>Thank you for completing your burnout assessment. Below is your comprehensive personalized recovery report.</p>
                        <div class="report">
                            {report_content}
                        </div>
                        <p style="margin-top: 30px;"><strong>Important:</strong> This report is for informational purposes only and is not a substitute for professional medical or psychological advice.</p>
                    </div>
                    <div class="footer">
                        <p>© Burnout Score Checker | Take care of yourself</p>
                        <p>This email was sent because you completed a burnout assessment and purchased the full report.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        response = resend.Emails.send(params)
        logger.info(f"Report email sent successfully to {email}")
        return True, "Report sent successfully"
        
    except Exception as e:
        logger.error(f"Error sending report email: {e}")
        return False, f"Failed to send report email: {str(e)}"
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # MongoDB
    mongo_url: str = "mongodb://localhost:27017/burnout_checker"
    
    # Session
    session_secret_key: str
    session_expiry_hours: int = 24
    
    # OTP
    otp_expiry_minutes: int = 10
    otp_max_resend_attempts: int = 3
    
    # Email (Resend)
    resend_api_key: str
    from_email: str = "noreply@yourdomain.com"
    
    # Emergent LLM
    emergent_llm_key: Optional[str] = None
    
    # Gumroad
    gumroad_product_url: str = "https://parameswaran8.gumroad.com/l/burnout-report"
    app_base_url: str = "http://localhost:3000"
    
    # App
    app_url: str
    integration_proxy_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()
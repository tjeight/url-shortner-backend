from datetime import datetime

from src.templates.otp import OTP_EMAIL_TEMPLATE


# Helper Function to buld the otp
def build_otp_email(
    otp: str,
    user_name: str,
    app_name: str = "URL Shortener",
    expiry_minutes: int = 10,
) -> str:
    return OTP_EMAIL_TEMPLATE.format(
        app_name=app_name,
        user_name=user_name,
        otp=otp,
        expiry_minutes=expiry_minutes,
        current_year=datetime.now().year,
    )

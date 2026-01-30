"""
==============================================
📧 UTILS/EMAIL.PY - Email Sending Utility
==============================================
এখানে OTP email পাঠানোর code আছে।

⚠️ IMPORTANT: Production এ এটা properly setup করতে হবে!
আমি এখানে ২টা option দিচ্ছি:

1. CONSOLE MODE (Development): Email console এ print হবে
2. SMTP MODE (Production): সত্যিকারের email যাবে

Gmail SMTP ব্যবহার করতে চাইলে:
- Gmail এ 2-Factor Authentication ON করো
- App Password generate করো (Google Account → Security → App Passwords)
- সেই password .env এ দাও
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


# =============================================
# ⚙️ EMAIL CONFIG
# =============================================

# Email settings (.env থেকে নিচ্ছি)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # your-email@gmail.com
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # App Password
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@agroclima.com")

# Development mode: True হলে email console এ print হবে, send হবে না
DEV_MODE = os.getenv("EMAIL_DEV_MODE", "true").lower() == "true"


# =============================================
# 📨 EMAIL TEMPLATES
# =============================================

def get_otp_email_template(otp_code: str, purpose: str = "verify") -> tuple[str, str]:
    """
    সুন্দর HTML email template তৈরি করে
    
    Args:
        otp_code: 6 digit OTP
        purpose: "verify" (signup এর পর) বা "reset" (password reset)
    
    Returns: (subject, html_body)
    """
    
    if purpose == "verify":
        subject = "🌿 AgroClima - Verify Your Email"
        title = "Verify Your Email"
        message = "Welcome to AgroClima! Please use the following code to verify your email address."
    else:  # reset
        subject = "🔐 AgroClima - Password Reset Code"
        title = "Reset Your Password"
        message = "You requested to reset your password. Use the following code to proceed."
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #1a1a1a; color: #ffffff; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; color: #4ade80; font-size: 28px; margin-bottom: 20px; }}
            .card {{ background-color: #2d2d2d; border-radius: 10px; padding: 30px; }}
            .title {{ font-size: 22px; margin-bottom: 10px; }}
            .message {{ color: #9ca3af; margin-bottom: 25px; }}
            .otp-box {{ background-color: #1a1a1a; border-radius: 8px; padding: 20px; text-align: center; }}
            .otp-code {{ font-size: 36px; letter-spacing: 10px; color: #4ade80; font-weight: bold; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            .warning {{ color: #f87171; font-size: 14px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">🌿 AgroClima</div>
            <div class="card">
                <div class="title">{title}</div>
                <div class="message">{message}</div>
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                <div class="warning">⏰ This code will expire in 10 minutes.</div>
            </div>
            <div class="footer">
                If you didn't request this, please ignore this email.
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html


# =============================================
# 📤 SEND EMAIL FUNCTIONS
# =============================================

async def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Email পাঠায়
    
    DEV_MODE=true হলে console এ print করে
    DEV_MODE=false হলে সত্যিকারের email পাঠায়
    
    Returns: True if success, False otherwise
    """
    
    # ========================
    # 🧪 DEVELOPMENT MODE
    # ========================
    if DEV_MODE:
        print("\n" + "="*50)
        print("📧 EMAIL (DEV MODE - Not actually sent)")
        print("="*50)
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-"*50)
        # Just show the OTP code for easy testing
        import re
        otp_match = re.search(r'class="otp-code">(\d{6})', html_body)
        if otp_match:
            print(f"🔢 OTP CODE: {otp_match.group(1)}")
        print("="*50 + "\n")
        return True
    
    # ========================
    # 📨 PRODUCTION MODE
    # ========================
    try:
        # Email message তৈরি
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        
        # HTML body attach
        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)
        
        # SMTP server এ connect করে email পাঠানো
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False


async def send_otp_email(to_email: str, otp_code: str, purpose: str = "verify") -> bool:
    """
    OTP email পাঠায়
    
    Args:
        to_email: যাকে পাঠাবে
        otp_code: 6 digit OTP
        purpose: "verify" বা "reset"
    """
    subject, html_body = get_otp_email_template(otp_code, purpose)
    return await send_email(to_email, subject, html_body)
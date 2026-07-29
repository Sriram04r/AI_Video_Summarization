import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_verification_email(to_email: str, code: str):
    """
    Sends a 6-digit verification code to the user's email.
    Requires SMTP_EMAIL and SMTP_PASSWORD in the .env file.
    """
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        logger.warning(f"SMTP credentials missing! Could not send email to {to_email}. Verification Code: {code}")
        return False
        
    try:
        # Setup the MIME
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Password Reset Code"
        message["From"] = f"AI Video Summarization <{sender_email}>"
        message["To"] = to_email

        # Create the HTML version of the message
        html = f"""\
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4f46e5;">Password Reset Request</h2>
            <p>You have requested to reset your password.</p>
            <p>Your 6-digit verification code is:</p>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; letter-spacing: 5px; color: #1f2937; margin: 20px 0;">
              {code}
            </div>
            <p style="color: #6b7280; font-size: 14px;">This code will expire in 15 minutes.</p>
            <p style="color: #6b7280; font-size: 14px;">If you did not request a password reset, please ignore this email.</p>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)

        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
            
        logger.info(f"Verification email successfully sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}")
        return False

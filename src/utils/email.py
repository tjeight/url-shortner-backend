import logging

import resend

from src.configs.settings import settings

logger = logging.getLogger(__name__)


# Helper Function to send the emaik
async def send_email(to: str, subject: str, html_content: str) -> bool:
    try:
        response = resend.Emails.send(
            {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html_content,
            }
        )
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        return False
    logger.info(f"Email sent successfully to {to}. Response: {response}")
    return True

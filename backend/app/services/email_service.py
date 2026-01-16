"""
Email service for sending notifications.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.host = settings.email_host
        self.port = settings.email_port
        self.user = settings.email_user
        self.password = settings.email_password
        self.from_addr = settings.email_from
        self.use_tls = settings.email_use_tls

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(
            self.host and
            self.port and
            self.from_addr
        )

    def _create_connection(self) -> smtplib.SMTP:
        """Create and return an SMTP connection."""
        if self.use_tls:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
        else:
            server = smtplib.SMTP(self.host, self.port)

        if self.user and self.password:
            server.login(self.user, self.password)

        return server

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping send")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = to

            # Add plain text part
            msg.attach(MIMEText(body, "plain"))

            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            server = self._create_connection()
            server.sendmail(self.from_addr, to, msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    def send_backup_failure_alert(
        self,
        error_message: str,
        to: Optional[str] = None
    ) -> bool:
        """
        Send a backup failure alert email.

        Args:
            error_message: Description of the backup failure
            to: Recipient email (uses settings.email_to if not provided)

        Returns:
            True if sent successfully, False otherwise
        """
        recipient = to or settings.email_to

        if not recipient:
            logger.warning("No recipient configured for backup alerts")
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = "[HomeRegistry] Backup Failed"

        body = f"""HomeRegistry Backup Failure Alert

Time: {timestamp}
Error: {error_message}

Please check the backup system and ensure the database is being backed up properly.

---
This is an automated message from HomeRegistry.
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .alert {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 5px; }}
        .alert h2 {{ color: #721c24; margin-top: 0; }}
        .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 3px; margin: 15px 0; }}
        .footer {{ color: #6c757d; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="alert">
        <h2>Backup Failed</h2>
        <p>The HomeRegistry backup system encountered an error.</p>
        <div class="details">
            <strong>Time:</strong> {timestamp}<br>
            <strong>Error:</strong> {error_message}
        </div>
        <p>Please check the backup system and ensure the database is being backed up properly.</p>
    </div>
    <div class="footer">
        This is an automated message from HomeRegistry.
    </div>
</body>
</html>
"""

        return self.send_email(recipient, subject, body, html_body)

    def send_backup_success_notification(
        self,
        backup_info: dict,
        to: Optional[str] = None
    ) -> bool:
        """
        Send a backup success notification (optional, for testing).

        Args:
            backup_info: Dict with backup metadata
            to: Recipient email (uses settings.email_to if not provided)

        Returns:
            True if sent successfully, False otherwise
        """
        recipient = to or settings.email_to

        if not recipient:
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = "[HomeRegistry] Backup Successful"

        body = f"""HomeRegistry Backup Success

Time: {timestamp}
Filename: {backup_info.get('filename', 'N/A')}
Size: {backup_info.get('size', 0)} bytes

---
This is an automated message from HomeRegistry.
"""

        return self.send_email(recipient, subject, body)


# Singleton instance
email_service = EmailService()

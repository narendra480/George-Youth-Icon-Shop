import logging
from abc import ABC, abstractmethod

from app.core.config import settings


class EmailService(ABC):
    @abstractmethod
    def send_verification_email(self, recipient_email: str, verification_token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_password_reset_email(self, recipient_email: str, reset_token: str) -> None:
        raise NotImplementedError


class ConsoleEmailService(EmailService):
    def __init__(self) -> None:
        self.logger = logging.getLogger("app.services.email_service")

    def send_verification_email(self, recipient_email: str, verification_token: str) -> None:
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"
        self.logger.info(
            "Sending verification email to %s with link %s",
            recipient_email,
            verification_url,
        )

    def send_password_reset_email(self, recipient_email: str, reset_token: str) -> None:
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        self.logger.info(
            "Sending password reset email to %s with link %s",
            recipient_email,
            reset_url,
        )


def get_email_service() -> EmailService:
    if settings.email_backend == "console":
        return ConsoleEmailService()
    return ConsoleEmailService()

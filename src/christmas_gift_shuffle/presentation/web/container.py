import streamlit as st

from christmas_gift_shuffle.application.services import GiftExchangeService
from christmas_gift_shuffle.infrastructure.dependencies import create_repository
from christmas_gift_shuffle.application.services.notification_service import AssignmentNotificationService
from christmas_gift_shuffle.infrastructure.smtp_email_sender import SmtpEmailSender
from christmas_gift_shuffle.infrastructure.mailing.renderer import JinjaAssignmentEmailRenderer


def get_notification_service() -> AssignmentNotificationService:
    cfg = st.secrets["email"]
    sender = SmtpEmailSender(cfg["host"], int(cfg["port"]), cfg["username"], cfg["password"])
    return AssignmentNotificationService(sender, JinjaAssignmentEmailRenderer())

@st.cache_resource
def get_repository():
    return create_repository()


def get_service() -> GiftExchangeService:
    return GiftExchangeService(get_repository())
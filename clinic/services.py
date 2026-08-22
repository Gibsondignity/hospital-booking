"""Small reusable services shared across clinic modules."""

import logging
from dataclasses import dataclass

import requests
from django.conf import settings
from django.db import transaction

from .models import AuditLog, IdentifierSequence

logger = logging.getLogger(__name__)
SENSITIVE_KEYS = {"password", "secret", "api_key", "token", "clinical_notes", "diagnosis"}


def next_identifier(*, key, prefix):
    with transaction.atomic():
        sequence, _ = IdentifierSequence.objects.select_for_update().get_or_create(key=key)
        value = sequence.next_value
        sequence.next_value = value + 1
        sequence.save(update_fields=["next_value"])
        return f"{prefix}-{value:06d}"


def log_event(*, actor, action, resource, metadata=None):
    safe_metadata = {key: value for key, value in (metadata or {}).items() if key.lower() not in SENSITIVE_KEYS}
    return AuditLog.objects.create(actor=actor if getattr(actor, "is_authenticated", False) else None, action=action, resource_type=resource._meta.label_lower, resource_id=str(resource.pk), metadata=safe_metadata)


@dataclass(frozen=True)
class SMSResult:
    successful: bool
    provider: str
    detail: str = ""


def normalise_ghana_phone(phone):
    value = "".join(character for character in phone if character.isdigit() or character == "+")
    if value.startswith("0"):
        return "+233" + value[1:]
    if value.startswith("233"):
        return "+" + value
    return value


def send_sms(*, recipient, message, sender=None):
    """Provider boundary only; scheduling and reminder automation are later phases."""
    provider = getattr(settings, "SMS_PROVIDER", "arkesel")
    api_key = getattr(settings, "ARKESSEL_API_KEY", "")
    if not api_key:
        logger.warning("SMS not sent because the provider has not been configured.")
        return SMSResult(False, provider, "SMS provider is not configured.")
    if provider != "arkesel":
        return SMSResult(False, provider, "Unsupported SMS provider.")
    try:
        response = requests.get("https://sms.arkesel.com/sms/api", params={"action": "send-sms", "api_key": api_key, "from": sender or settings.ARKESSEL_SENDER_ID, "to": normalise_ghana_phone(recipient), "sms": message}, timeout=15)
        response.raise_for_status()
        return SMSResult(True, provider, "Message accepted by provider.")
    except requests.RequestException:
        logger.error("SMS provider request failed without recording provider credentials.")
        return SMSResult(False, provider, "SMS provider request failed.")

"""Privacy boundary and deterministic policy for appointment notifications."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class AppointmentEvent(StrEnum):
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class NotificationPlan:
    prompt: str
    channel: str
    requires_staff_follow_up: bool


def plan_notification(
    *, event: AppointmentEvent, starts_at: datetime, clinic_phone: str
) -> NotificationPlan:
    """Build an operational prompt with no patient identifiers or clinical details."""
    starts = starts_at.isoformat()
    instructions = (
        "Write one calm appointment notification. State only the appointment status, "
        f"time {starts}, and clinic phone {clinic_phone}. Do not infer or mention a "
        "diagnosis, treatment, clinician, patient identity, or medical record. "
        "Do not give medical advice."
    )
    if event is AppointmentEvent.CANCELLED:
        return NotificationPlan(
            prompt=f"{instructions} The appointment was cancelled. Ask the patient to call.",
            channel="sms",
            requires_staff_follow_up=True,
        )
    if event is AppointmentEvent.RESCHEDULED:
        return NotificationPlan(
            prompt=f"{instructions} The appointment was rescheduled. Ask for confirmation.",
            channel="sms",
            requires_staff_follow_up=False,
        )
    return NotificationPlan(
        prompt=f"{instructions} The appointment is confirmed.",
        channel="sms",
        requires_staff_follow_up=False,
    )


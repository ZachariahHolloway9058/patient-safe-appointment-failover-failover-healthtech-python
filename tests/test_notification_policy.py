from datetime import datetime, timezone

from notification_policy import AppointmentEvent, plan_notification


def test_cancelled_appointment_requires_safe_staff_follow_up() -> None:
    plan = plan_notification(
        event=AppointmentEvent.CANCELLED,
        starts_at=datetime(2027, 1, 12, 9, 30, tzinfo=timezone.utc),
        clinic_phone="+1-555-0100",
    )

    assert plan.requires_staff_follow_up is True
    assert plan.channel == "sms"
    assert "cancelled" in plan.prompt
    assert "call" in plan.prompt
    assert "diagnosis" in plan.prompt
    assert "patient identity" in plan.prompt


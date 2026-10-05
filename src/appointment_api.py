"""Executable appointment operations API."""

from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel, Field

from infrai_gateway import draft_notification
from notification_policy import AppointmentEvent, plan_notification

app = FastAPI(title="Appointment notification service")


class AppointmentNotificationRequest(BaseModel):
    event: AppointmentEvent
    starts_at: datetime
    clinic_phone: Annotated[str, Field(min_length=7, max_length=24)]


class AppointmentNotificationResponse(BaseModel):
    message: str
    channel: str
    requires_staff_follow_up: bool


@app.post("/appointment-notifications", response_model=AppointmentNotificationResponse)
def create_appointment_notification(
    request: AppointmentNotificationRequest,
) -> AppointmentNotificationResponse:
    plan = plan_notification(
        event=request.event,
        starts_at=request.starts_at,
        clinic_phone=request.clinic_phone,
    )
    try:
        message = draft_notification(plan.prompt)
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="Notification drafting is busy") from exc
    except APIStatusError as exc:
        status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=status, detail="Notification request rejected") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="Notification drafting unavailable") from exc
    return AppointmentNotificationResponse(
        message=message,
        channel=plan.channel,
        requires_staff_follow_up=plan.requires_staff_follow_up,
    )


from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .infrai_client import InfraiClient


@dataclass(frozen=True)
class CropRequest:
    image: str
    aspects: tuple[str, ...] = ("1:1", "4:5", "16:9")


@dataclass(frozen=True)
class Appointment:
    patient_name: str
    starts_at: str
    confirmed: bool


def crop_variants(request: CropRequest, client: InfraiClient) -> dict[str, Any]:
    return {aspect: client.crop(request.image, aspect) for aspect in request.aspects}


def patient_notification(appointment: Appointment) -> str:
    if appointment.confirmed:
        return f"预约已确认：{appointment.patient_name}，时间 {appointment.starts_at}。"
    return f"请联系诊所确认预约：{appointment.patient_name}，原定时间 {appointment.starts_at}。"


def prepare_media_job(request: CropRequest, client: InfraiClient, bucket: str = "clinic-media") -> dict[str, Any]:
    client.ensure_bucket(bucket)
    variants = crop_variants(request, client)
    upload = client.presign(bucket, "appointments/variants.json", "put")
    return {"variants": variants, "manifest_upload": upload, "status": "ready"}

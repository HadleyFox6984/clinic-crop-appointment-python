from src.healthtech_service import Appointment, patient_notification


def test_unconfirmed_appointment_gets_safe_actionable_message() -> None:
    appointment = Appointment("Lin", "2026-09-15 10:30", False)
    assert patient_notification(appointment) == "请联系诊所确认预约：Lin，原定时间 2026-09-15 10:30。"

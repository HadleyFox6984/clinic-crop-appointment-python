from .healthtech_service import Appointment, CropRequest, patient_notification


if __name__ == "__main__":
    appointment = Appointment("Mina", "2026-09-15 10:30", True)
    print(patient_notification(appointment))
    print(CropRequest("uploaded-image-id").aspects)

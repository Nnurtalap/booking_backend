from email.message import EmailMessage
from typing import Any, Dict

from pydantic import EmailStr

from app.config import settings


def create_booking_confirmation_template(
    booking: Dict[str, Any],
    email_to: EmailStr,
   
):

    email = EmailMessage()

    email['Subject'] = 'Подтверждение бронирования'
    email['From'] = settings.SMTP_USER
    email['To'] = email_to

    email.set_content(
        f"""
            <h1>Подтверждение бронирования</h1>
            Подтверждение бронирования отеля для с {booking['date_from']} до {booking['date_to']}
            

        """,
        subtype='html'
    )

    return email



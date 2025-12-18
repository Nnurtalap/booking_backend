import json
import smtplib
from pathlib import Path
from typing import Any, Dict

from PIL import Image
from pydantic import EmailStr

from app.config import settings
from app.tasks.celery import celery
from app.tasks.email_template import create_booking_confirmation_template


@celery.task
def process_pic(
    path: str
):
    im_path = Path(path)
    im = Image.open(im_path)
    im_resized_1000_500 = im.resize((1000, 500))
    im_resized_200_100 = im.resize((200, 100))

    filename = im_path.stem 

    im_resized_1000_500.save(f'app/static/image/resized_1000_500_{filename}.webp')
    im_resized_200_100.save(f'app/static/image/resized_200_100_{filename}.webp')


@celery.task
def send_booking_confirmation_email(
    booking: Dict[str, Any],
    email_to: EmailStr
): 

    if isinstance(booking, str):
        booking = json.loads(booking)

    msq_content = create_booking_confirmation_template(booking, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_POST) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msq_content)

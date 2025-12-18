from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import parse_obj_as

from app.booking.dao import BookingDAO
from app.booking.shemas import SBooking
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users
from fastapi_versioning import version

router = APIRouter(
    prefix='/bookings',
    tags=['Bookings']
)

@router.post('')
@version(1)
async def add_bookings(
    room_id: int,
    date_from: date, 
    date_to: date,

    user: Users = Depends(get_current_user)): 

    booking = await BookingDAO.add( user.id,room_id, date_from, date_to)
    booking_dict = {
        'room_id': room_id,
        'user_id': user.id,
        'date_from': str(date_from),
        'date_to': str(date_to),
    }
    if booking == None:
        raise RoomCannotBeBooked
    
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return {"booking_id": booking.id}



@router.delete('/{booking_id}')
@version(1)
async def delete_bookings(booking_id:int, user: Users = Depends(get_current_user)):
    await BookingDAO.delete(booking_id=booking_id, user_id=user.id) 
    


@router.get('')
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.get_user_bookings(user.id)
     


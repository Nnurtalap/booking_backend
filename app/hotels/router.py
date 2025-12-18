from datetime import date

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.hotels.dao import HotelDAO

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("")
async def get_hotel_by_location_and_time(
    location: str, date_from: date, date_to: date
):
    return await HotelDAO.get_hotel_by_location_and_time(
        location=location, date_from=date_from, date_to=date_to
    )

@router.get("/{hotel_id}/rooms")
async def get_rooms_by_hotel_id(hotel_id: int, date_from: date, date_to: date):
    return await HotelDAO.get_rooms_by_hotel_id(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )


@router.get("/{hotel_id}")
# @cache(expire=30)
async def get_hotel_by_id(hotel_id: int):
    return await HotelDAO.get_hotel_by_id(hotel_id=hotel_id)



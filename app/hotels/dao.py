from datetime import date

from sqlalchemy import and_, func, select

from app.booking.models import Booking
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.logger import logger 

class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_hotel_by_id(cls, hotel_id: int):
        try:
            async with async_session_maker() as session:
                get_hotel = select(cls.model).where(cls.model.id==hotel_id)
                result = await session.execute(get_hotel)
                hotel = result.scalar()

                if hotel is None:
                    raise HTTPException(status_code=409)
                return hotel
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            if isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"

            extra = {
                'hotel_id': hotel_id
            }
            logger.error(msg, extra=extra, exc_info=True)
            

    @classmethod
    async def get_rooms_by_hotel_id(cls, hotel_id: int, date_from: date, date_to: date):
        try:
            async with async_session_maker() as session:
                if date_from >= date_to:
                    raise HTTPException(status_code=400, detail="Дата заезда должна быть раньше даты выезда")
                if (date_to - date_from).days > 30:
                    raise HTTPException(status_code=400, detail="Нельзя бронировать более чем на 30 дней")
            booked_rooms = select(
                Booking.room_id,
                func.count(Booking.room_id).label('booked_count')
            ).where(
                and_(
                    Booking.date_from < date_to,
                    Booking.date_to > date_from
                    )
            ).group_by(Booking.room_id).cte('booked_rooms')

            get_rooms = select(
                Rooms.id,
                Rooms.hotel_id, # Убедитесь, что Rooms.hotel_id существует
                Rooms.name,
                Rooms.description,
                Rooms.services,
                Rooms.price,
                Rooms.quantity,
                Rooms.image_id,

                (Rooms.quantity - func.coalesce(booked_rooms.c.booked_count, 0)).label('rooms_left'),
                (Rooms.price * (date_to - date_from).days).label('total_cost')
            ).join(
                booked_rooms,
                Rooms.id == booked_rooms.c.room_id,
                isouter=True
            ).where(
                Rooms.hotel_id==hotel_id
            )

            result = await session.execute(get_rooms)
            return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            if isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"

            extra = {
                'hotel_id': hotel_id,
                'date_from': date_from,
                'date_to': date_to
            }
            logger.error(msg, extra=extra, exc_info=True)
        
    @classmethod
    async def get_hotel_by_location_and_time(cls, location: str, date_from: date, date_to: date):
        try:
            async with async_session_maker() as session:
                if date_from >= date_to:
                    raise HTTPException(status_code=400, detail="Дата заезда должна быть раньше даты выезда")
                if (date_to - date_from).days > 30:
                    raise HTTPException(status_code=400, detail="Нельзя бронировать более чем на 30 дней")

                booked_rooms = select(
                    Booking.room_id,
                    func.count(Booking.room_id).label('booked_count')
                    ).where(
                        and_(
                            Booking.date_from < date_to,
                            Booking.date_to > date_from
                        )
                    ).group_by(Booking.room_id).cte('booked_rooms')
                
                rooms_available_per_room_type = (
                Rooms.quantity - func.coalesce(booked_rooms.c.booked_count, 0)
            )
                rooms_left_sum = func.sum(rooms_available_per_room_type)

                find_hotel = select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    # Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,

                    rooms_left_sum.label('rooms_left')
                    
                    ).join(
                        Rooms, 
                        Hotels.id == Rooms.hotel_id 
                    ).join(
                        booked_rooms, 
                        Rooms.id == booked_rooms.c.room_id, 
                        isouter=True
                    ).where(
                        Hotels.location.ilike(f'%{location}%')
                    ).group_by(
                        Hotels.id,
                        Hotels.name,
                        Hotels.location,
                        # Hotels.services,
                        Hotels.rooms_quantity,
                        Hotels.image_id,
                    ).having(
                        rooms_left_sum >= 1
                    )

                result = await session.execute(find_hotel)
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            if isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            extra = {
                'location': location,
                'date_from': date_from,
                'date_to': date_to
            }
            logger.error(msg, extra=extra, exc_info=True)

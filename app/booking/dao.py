from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.booking.models import Booking
from app.booking.shemas import SBooking
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine
from app.exceptions import RoomCannotBeBooked
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):

    model = Booking

    # select * from booking;

    # select * from rooms;

    # WITH booked_rooms as (
    # 	select * from booking
    # 	where room_id = 1 and
    # 	(date_from >= '2033-05-15' and date_from <= '2033-06-20') or
    # 	(date_from <= '2033-05-15' and date_to > '2033-05-15')
    # )
    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        
        try:
            if date_from >= date_to:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Дата заезда должна быть раньше даты выезда.",
                )

            if (date_to - date_from).days > 30:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Нельзя бронировать отель более чем на 30 дней.",
                )
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Booking)
                    .where(
                        and_(
                            Booking.room_id == room_id,
                            or_(
                                and_(
                                    Booking.room_id == room_id,
                                    Booking.date_from < date_to,
                                    Booking.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """

                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(
                        booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True
                    )
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # Рекомендую выводить SQL запрос в консоль для сверки
                # logger.debug(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                # logger.debug(f"{rooms_left=}")

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Booking)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(
                            Booking.id,
                            Booking.user_id,
                            Booking.room_id,
                            Booking.date_from,
                            Booking.date_to,
                        )
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.mappings().one()
                else:
                    raise RoomCannotBeBooked
        except RoomCannotBeBooked:
            raise RoomCannotBeBooked
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(
                msg, extra=extra, exc_info=True
            )

    @classmethod
    async def get_user_bookings(cls, user_id: int):
        """
        Получить все бронирования конкретного пользователя с вычисляемыми полями.
        Возвращает бронирования с подсчитанными total_days и total_cost.
        """
        try:
            async with async_session_maker() as session:
                # Запрос для получения бронирований пользователя с деталями
                query = (
                    select(
                        Booking.id,
                        Booking.room_id,
                        Booking.user_id,
                        Booking.date_from,
                        Booking.date_to,
                        Booking.price,
                        (Booking.date_to - Booking.date_from).label("total_days"),
                        (Booking.price * (Booking.date_to - Booking.date_from)).label(
                            "total_cost"
                        ),
                    )
                    .where(Booking.user_id == user_id)
                    .order_by(Booking.date_from.desc())
                )

                result = await session.execute(query)
                bookings = result.mappings().all()

                return bookings

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot retrieve user bookings"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot retrieve user bookings"

            extra = {"user_id": user_id}
            logger.error(msg, extra=extra, exc_info=True)
            raise

    @classmethod
    async def delete(cls, booking_id: int, user_id: int):
        try:
            async with async_session_maker() as session:
                stmt = (
                    delete(Booking)
                    .where(and_(Booking.id == booking_id, Booking.user_id == user_id))
                    .returning(Booking.id)
                )
                result = await session.execute(stmt)
                deleted_id = result.scalar()
                await session.commit()

                if not deleted_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Бронирование не найдено",
                    )

                return {"deleted_booking_id": deleted_id}

        except Exception as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot retrieve user bookings"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot retrieve user bookings"

            extra = {
                'booking_id': booking_id,
                'user_id': user_id
            }

            logger.error(msg, extra=extra, exc_info=True)
            raise

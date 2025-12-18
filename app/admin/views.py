from sqladmin import ModelView

from app.booking.models import Booking
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.users.models import Users


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email]
    column_details_exclude_list = [Users.hashed_password]
    can_delete = False
    name='Пользователи'
    name_plural = 'Пользователи'
    icon = 'fa-solid fa-user'



class BookingsAdmin(ModelView, model=Booking):
    column_list = [c.name for c in Booking.__table__.c] + [Booking.user]
    name='Бронь'
    name_plural = 'Брони'
    icon = 'fa-solid fa-user'

class RoomsAdmin(ModelView, model=Rooms):
    column_list = [c.name for c in Rooms.__table__.c] + [Rooms.hotel, Rooms.booking]
    name='Комнаты'
    name_plural = 'Комнаты'
    icon = 'fa-solid fa-bed'

class HotelAdmin(ModelView, model=Hotels):
    column_list = [c.name for c in Hotels.__table__.c] + [Hotels.room]
    name='Отели'
    name_plural = 'Отели'
    icon = 'fa-solid fa-hotel'
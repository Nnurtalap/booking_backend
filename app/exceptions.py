from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code=500
    detail=''

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlredyExistsException(BookingException): 
    status_code=status.HTTP_409_CONFLICT
    detail='пользователь уже зарегестрирован'


class InccorectEmailOrPassword(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='неверная почта или пароль'


class TokenExpiredException(BookingException): 
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Токен истек'
 

class TokenAbsetException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED 
    detail='Токен отсутствует'


class IncorrectTokenFormatException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Неверный формат токена'


class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED

class RoomCannotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='Не осталось свободных комнат'

class CannotAddDataToDatabase(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='не удалось добавить данные'

class CannotProcessCSV(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='Не удалось конвертировать данные'


from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import (IncorrectTokenFormatException, TokenAbsetException,
                            TokenExpiredException, UserIsNotPresentException)
from app.users.dao import UsersDAO


def get_token(request: Request):
    token = request.cookies.get('booking_access_token')

    if not token:
        raise TokenExpiredException
    
    return token 

async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )

    except JWTError:
        raise TokenAbsetException

    expire: str = payload.get('exp')
    if (not expire) or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise IncorrectTokenFormatException

    user_id: str = payload.get('sub')
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user


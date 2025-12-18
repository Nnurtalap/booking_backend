from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.exceptions import InccorectEmailOrPassword, UserAlredyExistsException
from app.users.auth import (authenticate_user, create_access_token,
                            get_password_hash)
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.shemas import SUserAuth

router = APIRouter(
    prefix='/auth',
    tags=['Auth & Users']
)


@router.post('/register')
async def register_user(user_date: SUserAuth):
    existing_user = await UsersDAO.find_one_or_none(email=user_date.email)

    if existing_user:
        raise UserAlredyExistsException
    
    hashed_password = get_password_hash(password=user_date.password)
    await UsersDAO.add(email=user_date.email, hashed_password=hashed_password)

@router.post('/login')
async def login_user(response: Response, user_date: SUserAuth):
    user = await authenticate_user(user_date.email, user_date.password)

    if not user:
        raise InccorectEmailOrPassword

    access_token = create_access_token({'sub': str(user.id)})
    response.set_cookie('booking_access_token', access_token, httponly=False)
    return access_token   


@router.post('/logout')
async def log_out(response: Response):
    response.delete_cookie('booking_access_token')

@router.get('/me')
async def info(current_user: Users = Depends(get_current_user)):
    return current_user





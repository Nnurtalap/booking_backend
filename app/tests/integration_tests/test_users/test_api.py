import pytest
from httpx import AsyncClient


@pytest.mark.parametrize('email,password,status_code', [
    ('nurta@gmail.com', 'Nurta07', 200),
    ('nurta@gmail.com', 'Nusrta07', 409),
    ('qqnurta@gmail.com', 'Nurta07', 200),
    ('nurta', 'Nurta07', 422)
])
async def test_register_user(email,password,status_code, ac: AsyncClient):
    result = await ac.post('/auth/register', json={
        'email': email,
        'password': password,
    })

    assert result.status_code == status_code


@pytest.mark.parametrize('email, password, status_code', [
    ('test@test.com', 'test', 200),
    ('artem@example.com', 'artem', 200),
    ('wrong@example.com', 'artem', 401)
])
async def test_login_user(email,password,status_code, ac: AsyncClient):
    response = await ac.post('/auth/login', json={
        'email': email,
        'password': password,
    })

    assert response.status_code == status_code
import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("location,date_from,date_to,status_code, detail", [
    ("Алтай", "2023-01-01", "2022-01-10", 400, "Дата заезда должна быть раньше даты выезда"),
    ("Алтай", "2023-01-01", "2023-02-10", 400, "Нельзя бронировать более чем на 30 дней"),
    ("Алтай", "2023-01-01", "2023-01-10", 200, None),
])
async def test_get_hotels_by_location_and_time(
    location,
    date_from,
    date_to,
    status_code,
    detail,
    ac: AsyncClient,
):
    response = await ac.get(
        "/v1/hotels", 
        params={
            'location': location,
            "date_from": date_from,
            "date_to": date_to,
        })
    assert response.status_code == status_code
    if str(status_code).startswith("4"):
        assert response.json()["detail"] == detail


@pytest.mark.parametrize('hotel_id, date_from, date_to, status_code', [
    (1, "2023-01-01", "2023-01-10", 200),
    (1, "2023-01-01", "2023-02-01", 400),
    (1, "2023-01-01", "2023-01-15", 200),
    (1, "2023-01-01", "2022-01-10", 400),
    (1, "2023-01-01", "2022-02-20", 400)


])
async def test_get_rooms_by_hotel_id(hotel_id, date_from, date_to,status_code, ac: AsyncClient):
    response = await ac.get(f'/v1/hotels/{hotel_id}/rooms', params={
        'hotel_id': hotel_id,
        'date_from': date_from,
        'date_to': date_to
    })

    assert response.status_code == status_code


@pytest.mark.parametrize('hotel_id, status_code', [
    (1, 200),
    (18, 409),
    (1, 200),
    (15, 409)
])
async def test_get_hotel_by_id(hotel_id, status_code, ac: AsyncClient):
    response = await ac.get(f'/v1/hotels/{hotel_id}', params={
        'hotel_id': hotel_id,
    })

    assert response.status_code == status_code
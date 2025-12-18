from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize('room_id, date_from, date_to ,booked_rooms, status_code', [
                            (1, "2025-05-01", "2025-05-15", 3 ,200),
                            # (1, "2025-05-01", "2025-05-15", 4 ,200),
                            # (1, "2025-05-01", "2025-05-15", 5 ,200),
                            # (1, "2025-05-01", "2025-05-15", 6 ,200),
                            # (1, "2025-05-01", "2025-05-15", 7 ,200),


                            
                            # (1, "2025-05-01", "2025-05-15", 7,409),
                            # (1, "2025-05-01", "2025-05-15", 7 ,409),

                            ]

                         )
async def test_add_and_get_booking(room_id, date_to, date_from, booked_rooms, status_code, authenticated_ac: AsyncClient):
    response = await authenticated_ac.post('/bookings', params={
        'room_id': room_id,
        'date_to': date_to, 
        'date_from': date_from
    })

    assert response.status_code == status_code

    response = await authenticated_ac.get('/bookings')

    assert len(response.json()) == booked_rooms
    



async def test_get_and_delete_booking(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/bookings")
    existing_bookings = [booking['id'] for booking in response.json()]
    for booking_id in existing_bookings:
        await authenticated_ac.delete(f'/bookings/{booking_id}')

    response = await authenticated_ac.get("/bookings")

    assert len(response.json()) == 0
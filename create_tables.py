import asyncio
from app.database import engine, Base

# Импортируйте ВСЕ модели
from app.users.models import Users
from app.booking.models import Booking
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
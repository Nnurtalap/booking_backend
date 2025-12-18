from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import time
import sentry_sdk

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin
from fastapi_versioning import VersionedFastAPI

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelAdmin, RoomsAdmin, UserAdmin
from app.booking.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.router import router as hotels_router
from app.images.router import router as router_images
from app.pages.router import router as router_pages
from app.users.router import router as users_router
from app.logger import logger
from app.importer.router import router as imports_router
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn="https://1e8ec0f884f247c01e5b9865b6efd401@o4510515418300416.ingest.de.sentry.io/4510515425706064",
    send_default_pii=True,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


# 1. Создаём базовое приложение
app = FastAPI(lifespan=lifespan)

# 2. Подключаем роутеры
app.include_router(router_images)
app.include_router(users_router)
app.include_router(router_bookings)
app.include_router(hotels_router)
app.include_router(router_pages)
app.include_router(imports_router)

# 3. Добавляем CORS
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization" 
    ],
)

# 4. Middleware ДО VersionedFastAPI
@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    time_start = time.perf_counter()
    response = await call_next(request)
    time_process = time.perf_counter() - time_start
    logger.info('Request handling time', extra={
        'process time': time_process
    })
    return response



# 5. ПРИМЕНЯЕМ ВЕРСИОНИРОВАНИЕ (без static!)
app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format='/v{major}'
)
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],

)
Instrumentator().instrument(app).expose(app)



# 6. Static файлы ПОСЛЕ VersionedFastAPI
app.mount('/static', StaticFiles(directory='app/static'), name='static')


# 7. Admin ПОСЛЕ версионирования
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(HotelAdmin)
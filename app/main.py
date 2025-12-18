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
from app.logger import logger
from app.importer.router import router as imports_router
from prometheus_fastapi_instrumentator import Instrumentator
from app.users.router import router_auth, router_users
from app.images.router import router as router_images
from app.importer.router import router as router_import
from app.prometheus.router import router as router_prometheus

app = FastAPI(
    title="Бронирование Отелей",
    version="0.1.0",
    root_path="/api",
)


if settings.MODE != "TEST":
    # Подключение Sentry для мониторинга ошибок. Лучше выключать на период локального тестирования
    sentry_sdk.init(
        dsn='https://1e8ec0f884f247c01e5b9865b6efd401@o4510515418300416.ingest.de.sentry.io/4510515425706064',
        traces_sample_rate=1.0,
    )


# Включение основных роутеров
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(hotels_router)
app.include_router(router_bookings)

# Включение дополнительных роутеров
app.include_router(router_images)
app.include_router(router_prometheus)
app.include_router(router_import)


# Подключение CORS, чтобы запросы к API могли приходить из браузера 
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js 
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", 
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)


# Подключение версионирования
app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/api/v{major}',
)

app.include_router(router_pages)

if settings.MODE == "TEST":
    # При тестировании через pytest, необходимо подключать Redis, чтобы кэширование работало.
    # Иначе декоратор @cache из библиотеки fastapi-cache ломает выполнение кэшируемых эндпоинтов.
    # Из этого следует вывод, что сторонние решения порой ломают наш код, и это бывает проблематично поправить.
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")

@app.on_event("startup")
def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


# Подключение эндпоинта для отображения метрик для их дальнейшего сбора Прометеусом
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


# Подключение админки
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(HotelAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)

app.mount("/static", StaticFiles(directory="app/static"), "static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    logger.info("Request handling time", extra={
        "process_time": round(process_time, 4)
    })
    return response

# Вы можете заметить один из минусов FastAPI -- вся конфигурация происходит
# в одном файле. Порой он может довольно сильно разрастаться.

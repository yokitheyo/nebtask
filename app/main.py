from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import buildings, activities, organizations
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    organizations.router,
    prefix=f"{settings.API_V1_STR}/organizations",
    tags=["organizations"],
)
app.include_router(
    buildings.router, prefix=f"{settings.API_V1_STR}/buildings", tags=["buildings"]
)
app.include_router(
    activities.router, prefix=f"{settings.API_V1_STR}/activities", tags=["activities"]
)


@app.get("/")
async def root():
    return {
        "message": "Тестовое задание справочник организаций. Документация доступна по адресу /docs"
    }

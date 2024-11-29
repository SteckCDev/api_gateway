from fastapi import APIRouter

from .v1 import v1_service_router as v1_service_router


service_routers: tuple[APIRouter, ...] = (v1_service_router,)

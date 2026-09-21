from fastapi import APIRouter
from app.api.endpoints import auth, users, courts, notifications, bookings, friends

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(courts.router, tags=["courts"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
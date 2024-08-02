from fastapi import APIRouter

from app.api.routes import items, login, users, utils, listings, transactions, messages, notifications, reports, reviews

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])

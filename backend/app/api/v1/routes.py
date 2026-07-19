from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.inventory import router as inventory_router
from app.routers.products import router as products_router
from app.routers.users import router as users_router
from app.routers.shop_settings import router as shop_settings_router
from app.routers.cart import router as cart_router
from app.routers.wishlist import router as wishlist_router
from app.routers.banners import router as banners_router
from app.routers.coupons import router as coupons_router
from app.routers.reviews import router as reviews_router
from app.routers.addresses import router as addresses_router
from app.routers.orders import router as orders_router
from app.routers.payments import router as payments_router
from app.routers.analytics import router as analytics_router
from app.routers.loyalty import router as loyalty_router
from app.routers.recommendations import router as recommendations_router
from app.routers.vendors import router as vendors_router
from app.routers.notifications import router as notifications_router


api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(products_router)
api_router.include_router(inventory_router)
api_router.include_router(shop_settings_router)
api_router.include_router(cart_router)
api_router.include_router(wishlist_router)
api_router.include_router(banners_router)
api_router.include_router(coupons_router)
api_router.include_router(reviews_router)
api_router.include_router(addresses_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(analytics_router)
api_router.include_router(loyalty_router)
api_router.include_router(recommendations_router)
api_router.include_router(vendors_router)
api_router.include_router(notifications_router)
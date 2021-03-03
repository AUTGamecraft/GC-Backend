from django.urls import path , include
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
    PresenterViweSet,
    CouponViewSet
)

router = routers.SimpleRouter()
router.register(r'talk' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register(r'service',UserServicesViewSet)
router.register(r'presenter',PresenterViweSet)
router.register(r'coupon',CouponViewSet)

urlpatterns = [
    path('' , include(router.urls)),
]
from django.urls import path
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
    PresenterSerializer
)

router = routers.SimpleRouter()
router.register(r'talks' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register('service',UserServicesViewSet)
router.register('presenter',UserServicesViewSet)

urlpatterns = router.urls

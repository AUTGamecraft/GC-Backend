from django.urls import path
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
)

router = routers.SimpleRouter()
router.register(r'talks' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register('service',UserServicesViewSet)


urlpatterns = router.urls

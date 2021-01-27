from django.urls import path
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
    PresenterViweSet
)

router = routers.SimpleRouter()
router.register(r'talk' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register(r'service',UserServicesViewSet)
router.register(r'presenter',PresenterViweSet)

urlpatterns = router.urls

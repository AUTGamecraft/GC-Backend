from django.urls import path
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
    CompetitionsViewSet
)

router = routers.SimpleRouter()
router.register(r'talk' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register(r'user_services' , UserServicesViewSet)
router.register(r'competition' , CompetitionsViewSet)

urlpatterns = router.urls

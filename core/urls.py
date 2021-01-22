from django.urls import path
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet
)

router = routers.SimpleRouter()
router.register(r'talks' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)


urlpatterns = router.urls

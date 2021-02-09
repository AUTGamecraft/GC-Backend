from django.urls import path
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
    PresenterViweSet,
    CompetitionMemberViewSet,
    TeamViewSet
)

router = routers.SimpleRouter()
router.register(r'talk' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register(r'service',UserServicesViewSet)
router.register(r'presenter',PresenterViweSet)
router.register(r'team',TeamViewSet)
router.register(r'member',CompetitionMemberViewSet)

urlpatterns = router.urls

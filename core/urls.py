from django.urls import path , include
from rest_framework import routers
from .views import (
    TalkViewSet,
    WorkshopViewSet,
    UserServicesViewSet,
    PresenterViweSet,
    CompetitionMemberViewSet,
    TeamViewSet,
    VerifyTeamRequestView
)

router = routers.SimpleRouter()
router.register(r'talk' , TalkViewSet)
router.register(r'workshop' , WorkshopViewSet)
router.register(r'service',UserServicesViewSet)
router.register(r'presenter',PresenterViweSet)
router.register(r'team',TeamViewSet)
router.register(r'member',CompetitionMemberViewSet)

urlpatterns = [
    path('' , include(router.urls)),
    path('team/join/<tid>/<mid>' , VerifyTeamRequestView.as_view(),name='request-team-activation')
]
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    UserViewSet,
    VerfiyUserView,
    TeamViewSet,
    VerifyTeamRequestView,
    VerfiyResetPasswordUserView,
)


router = SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'team', TeamViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('activation/<uid>', VerfiyUserView.as_view(), name='activation'),
    path('team/join/<tid>/<mid>', VerifyTeamRequestView.as_view(),
         name='request-team-activation'),
    path('activation/reset-pass/<uid>',
         VerfiyResetPasswordUserView.as_view(), name='reset-pass-activation')
]

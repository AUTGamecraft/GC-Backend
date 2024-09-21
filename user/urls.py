from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    UserViewSet,
    VerifyUserView,
    TeamViewSet,
    VerifyTeamRequestView,
    VerifyResetPasswordUserView,
)


router = SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'team', TeamViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('activation/<uid>', VerifyUserView.as_view(), name='activation'),
    path('team/join/<tid>/<mid>', VerifyTeamRequestView.as_view(),
         name='request-team-activation'),
    path('activation/reset-pass/<uid>',
         VerifyResetPasswordUserView.as_view(), name='reset-pass-activation')
]

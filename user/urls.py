from django.urls import path , include
from rest_framework.routers import SimpleRouter
from .views import (
    UserViewSet,
    VerfiyUserView
)


router = SimpleRouter()
router.register(r'users' ,UserViewSet )


urlpatterns = [
    path('' , include(router.urls)),
    path('activation/<uid>' , VerfiyUserView.as_view() , name='activation')
]

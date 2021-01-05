from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import (
    UserViewSet
)


router = SimpleRouter()
router.register(r'users' ,UserViewSet )


urlpatterns = router.urls

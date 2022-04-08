
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/' , include('core.urls')),
    path('api/v1/' , include('user.urls'))
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL , document_root= settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL , document_root= settings.STATIC_ROOT)
    

admin.site.index_title = "Game Craft"
admin.site.site_header = "Game Craft Admin"
admin.site.site_title = "GameCraft"
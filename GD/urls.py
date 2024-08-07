from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="AUT GameCraft docs",
        default_version='v2',
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[],
)

urlpatterns = [
    path('api/v2/admin/', admin.site.urls),
    path('api/v2/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v2/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v2/', include('core.urls')),
    path('api/v2/', include('user.urls')),
    path('api/v2/', include('game.urls'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path('docs<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.index_title = "Game Craft"
admin.site.site_header = "Game Craft Admin"
admin.site.site_title = "GameCraft"
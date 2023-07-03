from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import index


urlpatterns = [
    path('', index, name='HomePage'),
    path('blog/', include('Blog.urls')),
    path('users/', include('users.urls')),
    path("chat/", include("chat.urls")),
    path('admin/', admin.site.urls),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


























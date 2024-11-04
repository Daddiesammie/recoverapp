from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import RegisterView, custom_logout, ProfileUpdateView  # Updated import

urlpatterns = [
    path('admin/', include("django_admin_kubi.urls")),  # Keep this first
    path('admin/', admin.site.urls),  # This should come after django_admin_kubi
    path('', include('cases.urls')),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


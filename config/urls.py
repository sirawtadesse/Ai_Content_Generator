from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),        # home, about, services pages
    path('accounts/', include('accounts.urls')),  # login, logout, register
    path('blog/', include('blog.urls')),      # blog pages
    path('contact/', include('contact.urls')),  # contact form
    path('generate/', include('content.urls')),  # content generation page

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

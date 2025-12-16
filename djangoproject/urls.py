"""
URL configuration for inventorymgmt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('suppliers/', include('suppliers.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('inventorymgmt.urls')),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# During development, let Django's staticfiles app serve files from
# the app/static and project `static/` directories.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
else:
    # In production static files should be served by the web server
    # and `collectstatic` should populate `STATIC_ROOT`.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

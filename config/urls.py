"""
URL configuration for config project.

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
from django.conf.urls import handler404, handler500

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),  # Core app URLs
    path('residents/', include('apps.residents.urls')),
    path('certificates/', include('apps.certificates.urls')),
    path('blotter/', include('apps.blotter.urls')),
    path('business/', include('apps.business.urls')),
    path('finance/', include('apps.finance.urls')),
    path('audit/', include('apps.audit.urls')),
    path('gis/', include('apps.gis.urls')),  # GIS Map
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

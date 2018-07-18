"""registry URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.urls import include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from audit import views

urlpatterns = i18n_patterns(
    path('report/<int:org_pk>', views.report, name='report'),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('data_audit', views.data_audit, name='data_audit'),
    path('data_policy', views.data_policy, name='data_policy'),
    path('key_features', views.key_features, name='key_features'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('breach_detection', views.breach_detection, name='breach_detection'),
    path('breach_response', views.breach_response, name='breach_response'),
    path('create_report', views.create_report, name='create_report'),
    path('license', views.license, name='license'),
    path('i18n/', include('django.conf.urls.i18n')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # only for development

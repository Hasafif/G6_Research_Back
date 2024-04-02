from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('ath.urls')),
    path('',include('writing_tools.urls')),
]

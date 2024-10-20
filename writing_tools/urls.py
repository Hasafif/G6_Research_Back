from django.urls import  path,include
from . import views
urlpatterns = [

    path('campaign/',views.CampaignView.as_view(),name='campaign'),
]
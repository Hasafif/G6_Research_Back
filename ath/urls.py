from django.urls import  path,include
from . import views

urlpatterns = [
    # sign up and log in processors pages
    path('signup/',views.SignUpProcView.as_view(),name='signup'),
    path('login/',views.LoginProc.as_view(),name='login'),
    path('verify/',views.Verify.as_view(),name='verify'),
    # sign up and log in pages redirectors
    # Google sign in
    path('logout/',views.logout_proc,name='logout'),
    #path('send/',views.send_email,name='send_email'),
    path('social-auth/', include('social_django.urls',namespace='social')),
]

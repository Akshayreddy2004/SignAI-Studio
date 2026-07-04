from django.contrib import admin
from django.urls import path
from blogs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name="homepage"),
    path('contact/', views.contact, name="contact"),
    path('about/', views.about, name="about"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registration/', views.registration, name="registration"),
    path('userhome/', views.userhome, name="userhome"),
    path('studio/', views.studio, name="studio"),
    path('dictionary/', views.dictionary, name="dictionary"),
    path('api/log_translation/', views.log_translation, name="log_translation"),
    # Legacy desktop triggers
    path('audio_sign/', views.audio_sign, name="audio_sign"),
    path('sign_audio/', views.sign_audio, name="sign_audio"),
]

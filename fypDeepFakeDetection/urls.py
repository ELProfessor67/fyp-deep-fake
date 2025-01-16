from django.contrib import admin
from django.urls import path
from .views import Home, Image,Video,predict_page,About

urlpatterns = [
    path('',Home,name="home"),
    path('images/',Image,name="image"),
    path('videos/',Video,name="video"),
    path('predict/', predict_page, name='predict'),
    path('about/', About, name='about'),
    
]



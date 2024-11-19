from django.contrib import admin
from django.urls import path
from app import views


urlpatterns = [
    path("", views.index, name= "home"),
    path("log_in", views.log_in, name= "log_in"),
    path("register", views.register, name= "register"),
    path("dashboard", views.dashboard, name= "dashboard"),
    path("post_analysis", views.post_analysis, name= "post_analysis"),
    path("text_analysis", views.text_analysis, name= "text_analysis"),
    path("log_out", views.log_out, name= "log_out"),
]
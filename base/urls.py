from django.urls import path
from . import views
from django.contrib.auth import views as auth_views   # 使用內建登出功能


urlpatterns=[
    path('', views.home, name='home'),

    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # 使用內建登出功能，在views裡面就不用再轉寫登出函式邏輯

    path('rooms/', views.rooms, name='rooms'),
    path('room/<slug:slug>/', views.room, name='room'),
]

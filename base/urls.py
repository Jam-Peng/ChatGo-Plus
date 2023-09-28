from django.urls import path
from . import views
from django.contrib.auth import views as auth_views   # 使用內建登出功能


urlpatterns=[
    path('', views.home, name='home'),

    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),   # 使用內建登出功能，在views裡面就不用再轉寫登出函式邏輯

    path('rooms/', views.rooms, name='rooms'),                                                      # 手機版論壇頁
    path('room/<slug:slug>/', views.room, name='room'),                                             # 公開論壇的聊天室
    path('create-public-room/', views.createPublicRoom, name='create-public-room'),                 # 建立公開聊天室
    path('update-public-room/<slug:slug>/', views.updatePublicRoom, name='update-public-room'),     # 更新公開聊天室
    path('delete-public-room/<slug:slug>/', views.deletePublicRoom, name='delete-public-room'),     # 刪除公開聊天室

    path('private-room/<slug:slug>/', views.privateRoom, name='private-room'),                      # 與朋友的私人聊天室
    path('create-room/', views.createPrivateRoom, name='create-room'),                              # 建立私人聊天室方法
    path('delete-room/<slug:slug>/', views.deletePrivateRoom, name='delete-room'),

    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('update-user/', views.updateUser, name='update-user'),
]

from django.urls import path
from gridapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('scan', views.Scan.as_view(), name='scan_all'),
    path('add_to_db', views.AddServer.as_view(), name='add_to_db'),
    path('searchdb', views.SearchDB.as_view(), name='search'),

    path('', views.user, name='user'),
    path('gridadmin', views.gridadmin, name='grid-admin'),
    path('login', auth_views.LoginView.as_view(
        template_name='gridapp/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        template_name='gridapp/logout.html'), name='logout'),
    # path('search', views.ipscreen, name='ip-screen'),
    # path('singlescan', views.singlescan, name='singlescan'),
    path('add_asset', views.add_asset, name='add_asset'),
    # path('delete_asset', views.delete_asset, name='delete_asset'),



]

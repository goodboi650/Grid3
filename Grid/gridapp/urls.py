from django.urls import path
from gridapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('onerequest', views.SubmitOneRequest.as_view(), name='submit_one_request'),
    path('allrequest', views.SubmitAllRequest.as_view(), name='submit_all_request'),
    path('create_response', views.CreateResponse.as_view(), name='create_response'),
    path('delete', views.DeleteResponse.as_view(), name='delete'),
    path('search/', views.SearchResponse.as_view(), name='search'),

    path('', views.user, name='user'),
    path('gridadmin', views.gridadmin, name='grid-admin'),
    path('login', auth_views.LoginView.as_view(
        template_name='gridapp/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        template_name='gridapp/logout.html'), name='logout'),
    path('ipscreen', views.ipscreen, name='asset-list'),
    path('singlescan', views.singlescan, name='singlescan'),
    path('add_asset', views.add_asset, name='add_asset'),
    path('delete_asset', views.delete_asset, name='delete_asset'),



]

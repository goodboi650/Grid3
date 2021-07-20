from django.urls import path

from gridapp import views

urlpatterns = [
    path('onerequest/', views.SubmitOneRequest.as_view(),
         name='submit_one_request'),
    path('allrequest/', views.SubmitAllRequest.as_view(),
         name='submit_one_request'),
    path('create_response/', views.CreateResponse.as_view(), name='create_response'),
    path('delete/', views.DeleteResponse.as_view(), name='delete'),
    path('search/', views.SearchResponse.as_view(), name='search')
]

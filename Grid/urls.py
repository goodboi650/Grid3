from views import CreateResponse
from django.urls import path

from Grid import views

urlpatterns = [
    path('onerequest', views.SubmitOneRequest.as_view(), name='submit_one_request'),
    path('allrequest', views.SubmitAllRequest.as_view(), name='submit_one_request'),
    path('create_request', views.CreateResponse.as_view(), name='create_response')
]
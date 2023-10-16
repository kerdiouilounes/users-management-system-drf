from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user-retrieve-update-destroy'),
    path('me/', views.UserSelfRetrieveView.as_view(), name='user-self-retrieve'),
]
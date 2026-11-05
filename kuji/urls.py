from django.urls import path
from . import views


urlpatterns = [
    path('', views.kuji_list, name="kuji_list"),
    path('<uuid:pk>/', views.kuji_detail, name="kuji_detail"),
]

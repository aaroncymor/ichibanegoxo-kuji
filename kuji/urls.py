from django.urls import path
from . import views


urlpatterns = [
    path('', views.kuji_list, name="kuji_list"),
    path('marketplace/', views.marketplace, name="marketplace"),
    path('<uuid:pk>/', views.kuji_detail, name="kuji_detail"),
    path('<uuid:pk>/detail/', views.kuji_detail_new, name="kuji_detail_new"),
]

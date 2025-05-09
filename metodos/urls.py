from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('capitulo1/', views.capitulo1, name='capitulo1'),
    path('capitulo2/', views.capitulo2, name='capitulo2'),
    path('capitulo3/', views.capitulo3, name='capitulo3'),
    path('capitulo4/', views.capitulo4, name='capitulo4'),
]

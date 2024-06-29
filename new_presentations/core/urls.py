from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('title', views.get_title, name='title'),
    path('create', views.create_presentation, name='presentation'),
    path('download', views.download, name='download'),
    path('download_presentation', views.download_presentation,
         name='download_presentation')
]

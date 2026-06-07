from django.urls import path
from .views import (
    get_resolution, 
    convert_grayscale
)

urlpatterns = [
    path('get/resolution', get_resolution, name='get_resolution'),
    path('convert/grayscale', convert_grayscale, name='convert_grayscale'),
]
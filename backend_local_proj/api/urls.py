from django.urls import path
from .views import (
    chat_with_munch, 
    paint_image, 
    get_resolution, 
    convert_grayscale
)

urlpatterns = [
    path('chat', chat_with_munch, name='chat_with_munch'),
    path('paint', paint_image, name='paint_image'),
    path('get/resolution', get_resolution, name='get_resolution'),
    path('convert/grayscale', convert_grayscale, name='convert_grayscale'),
]
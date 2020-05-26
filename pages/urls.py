from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path(
        '',
        views.index,
        name='home',
    ),
    path(
        'create_dataset/',
        views.create_dataset,
        name='cd',
    ),
    #path(
    #    'video_feed',
    #    views.video_feed, 
    #    name='video_feed'
    #)
]
from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    #path(
    #    '',
    #    views.index,
    #    name='home',
    #),
    path(
        'create_dataset/',
        views.cds,
        name='cd',
    ),
    #path(
    #    'video_feed',
    #    views.video_feed, 
    #    name='video_feed'
    #)
    path(
        'train/',
        views.train,
        name='train'
    ),
    path(
        'detect/',
        views.detect,
        name='detect'
    ),
    path(
        '',
        views.Attend
    )
]
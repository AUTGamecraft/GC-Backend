from .views import TalkList
from django.urls import path

urlpatterns = [
    path('' , TalkList.as_view() , name='talk_list')
]

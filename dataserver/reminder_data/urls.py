from django.urls import path, include
from .views import *

urlpatterns = [
    path('user', user_view),
    path('todo', todo_view)
]
"""
URL mappings for the User API.
"""

from django.urls import path
from .views import CreateUserView, CreateTokenView, ManageUserView


app_name = "user_app"

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create"),
    path("token/", CreateTokenView.as_view(), name="token"), 
    path("me/", ManageUserView.as_view(), name="me"), 
]
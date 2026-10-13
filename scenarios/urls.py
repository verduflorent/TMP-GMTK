from django.urls import path
from . import views

app_name = "scenarios"

urlpatterns = [
    path("", views.library, name="library"),
    path("<uuid:pk>/", views.detail, name="detail"),
]

from django.urls import path
from . import views, document_api

app_name = "scenarios"

urlpatterns = [
    path("", views.library, name="library"),
    path("<uuid:pk>/", views.detail, name="detail"),
    path("<uuid:pk>/document/", document_api.document, name="document"),
    path("<uuid:pk>/layout/", document_api.save_layout, name="layout"),
]

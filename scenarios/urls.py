from django.urls import path
from . import views, document_api, archive_views, splash_upload

app_name = "scenarios"

urlpatterns = [
    path("", views.library, name="library"),
    path("verify/", archive_views.verify_archive, name="verify"),
    path("<uuid:pk>/splash/upload/", splash_upload.upload_splash, name="splash_upload"),
    path("import/", archive_views.import_archive, name="import"),
    path("<uuid:pk>/", views.detail, name="detail"),
    path("<uuid:pk>/export/", archive_views.export_scenario, name="export"),
    path("<uuid:pk>/delete/", views.delete_scenario, name="delete"),
    path("<uuid:pk>/document/", document_api.document, name="document"),
    path("<uuid:pk>/layout/", document_api.save_layout, name="layout"),
]

"""Authenticated image upload for scenario Splash blocks.

Requires CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET.
No files are stored on Render's ephemeral disk.
"""
import os
import uuid

import cloudinary
import cloudinary.uploader
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import Scenario

MAX_SPLASH_BYTES = 8 * 1024 * 1024
MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


@login_required
@require_POST
def upload_splash(request, pk):
    get_object_or_404(Scenario.objects.filter(owner=request.user), pk=pk)
    image = request.FILES.get("image")
    if image is None or image.size > MAX_SPLASH_BYTES or image.size == 0:
        return JsonResponse({"error": "Image absente ou supérieure à 8 Mio."}, status=400)
    if image.content_type not in MIME_TYPES:
        return JsonResponse({"error": "Format PNG, JPEG ou WebP requis."}, status=400)
    signature = image.read(16)
    image.seek(0)
    if not (signature.startswith(b"\x89PNG\r\n\x1a\n")
            or signature.startswith(b"\xff\xd8\xff")
            or signature.startswith(b"RIFF") and signature[8:12] == b"WEBP"):
        return JsonResponse({"error": "Fichier image invalide."}, status=400)
    cloud = os.environ.get("CLOUDINARY_CLOUD_NAME")
    key = os.environ.get("CLOUDINARY_API_KEY")
    secret = os.environ.get("CLOUDINARY_API_SECRET")
    if not all((cloud, key, secret)):
        return JsonResponse({"error": "Stockage des images non configuré."}, status=503)
    cloudinary.config(cloud_name=cloud, api_key=key, api_secret=secret, secure=True)
    try:
        result = cloudinary.uploader.upload(
            image, folder="tmp-gmtk/scenarios/" + str(request.user.pk),
            public_id=str(uuid.uuid4()), resource_type="image",
            overwrite=False, invalidate=False,
        )
    except Exception:
        return JsonResponse({"error": "Téléversement impossible. Réessaie plus tard."}, status=502)
    url = result.get("secure_url", "")
    if not url.startswith("https://res.cloudinary.com/"):
        return JsonResponse({"error": "Réponse du stockage invalide."}, status=502)
    return JsonResponse({"url": url})

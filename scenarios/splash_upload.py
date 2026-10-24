"""Private scenario Splash images stored in PostgreSQL, served by Django."""
import io

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import Scenario, ScenarioSplash

MAX_UPLOAD = 8 * 1024 * 1024
MAX_PIXELS = 24_000_000
MAX_SIDE = 1920
MAX_STORED = 2 * 1024 * 1024


@login_required
@require_POST
def upload_splash(request, pk):
    scenario = get_object_or_404(Scenario.objects.filter(owner=request.user), pk=pk)
    uploaded = request.FILES.get("image")
    if uploaded is None or not 0 < uploaded.size <= MAX_UPLOAD:
        return JsonResponse({"error": "Image absente ou supérieure à 8 Mio."}, status=400)
    try:
        with Image.open(uploaded) as source:
            if source.format not in ("PNG", "JPEG", "WEBP"):
                raise ValueError("Format d'image non pris en charge.")
            if source.width * source.height > MAX_PIXELS:
                raise ValueError("Image trop grande.")
            source.load()
            corrected = ImageOps.exif_transpose(source)
            corrected.thumbnail((MAX_SIDE, MAX_SIDE))
            if corrected.mode not in ("RGB", "RGBA"):
                corrected = corrected.convert("RGBA" if "A" in corrected.getbands() else "RGB")
            output = io.BytesIO()
            corrected.save(output, format="WEBP", quality=80, method=4)
            data = output.getvalue()
            if len(data) > MAX_STORED:
                raise ValueError("Image compressée trop volumineuse.")
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return JsonResponse({"error": "Image invalide ou trop volumineuse."}, status=400)
    splash = ScenarioSplash.objects.create(scenario=scenario, data=data)
    return JsonResponse({"url": f"/scenarios/{scenario.pk}/splash/{splash.pk}/"})


@login_required
@require_GET
def read_splash(request, pk, image_id):
    image = get_object_or_404(
        ScenarioSplash.objects.filter(scenario_id=pk, scenario__owner=request.user),
        pk=image_id,
    )
    response = HttpResponse(bytes(image.data), content_type=image.content_type)
    response["Cache-Control"] = "private, max-age=3600"
    response["X-Content-Type-Options"] = "nosniff"
    return response

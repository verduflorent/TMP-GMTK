import hashlib
import json
import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ScenarioForm
from toolkit.models import Encounter
from .models import Scenario, ScenarioCreateReceipt


@login_required
@require_http_methods(["GET", "POST"])
def library(request):
    if request.method == "POST":
        try:
            key = uuid.UUID(request.POST["creation_key"])
        except (KeyError, ValueError, TypeError):
            return HttpResponseBadRequest("Clé de création manquante ou invalide.")
        form = ScenarioForm(request.POST, owner=request.user)
        if form.is_valid():
            cleaned = form.cleaned_data
            fingerprint = hashlib.sha256(json.dumps({
                "title": cleaned["title"],
                "summary": cleaned["summary"],
                "folder": cleaned["folder"].pk if cleaned["folder"] else None,
            }, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
            # The unique (owner, key) constraint serializes duplicate submissions.
            # Lock the existing receipt, or create a new receipt and scenario atomically.
            with transaction.atomic():
                receipt, created = ScenarioCreateReceipt.objects.get_or_create(
                    owner=request.user, key=key,
                    defaults={"fingerprint": fingerprint},
                )
                receipt = ScenarioCreateReceipt.objects.select_for_update().get(pk=receipt.pk)
                if receipt.fingerprint != fingerprint:
                    return HttpResponse("Clé déjà utilisée pour une création différente.", status=409)
                if not created:
                    if receipt.scenario_id:
                        return HttpResponseRedirect(reverse("scenarios:detail", args=[receipt.scenario_id]))
                    return HttpResponse("Cette création a déjà été traitée et son scénario n'existe plus.", status=409)
                scenario = form.save(commit=False)
                scenario.owner = request.user
                scenario.full_clean()
                scenario.save()
                receipt.scenario = scenario
                receipt.save(update_fields=["scenario"])
            return HttpResponseRedirect(reverse("scenarios:detail", args=[scenario.pk]))
    else:
        form = ScenarioForm(owner=request.user)
    creation_key = str(uuid.uuid4())
    scenarios = Scenario.objects.filter(owner=request.user).select_related("folder").order_by("-updated_at")
    return render(request, "scenarios/library.html", {"scenarios": scenarios, "form": form, "creation_key": creation_key})


@login_required
@require_http_methods(["GET"])
def detail(request, pk):
    scenario = get_object_or_404(Scenario.objects.filter(owner=request.user), pk=pk)
    scenes = scenario.scenes.all()
    encounters = list(Encounter.objects.filter(owner=request.user).order_by("name").values("id", "name"))
    return render(request, "scenarios/detail.html", {"scenario": scenario, "scenes": scenes, "encounter_options": encounters})

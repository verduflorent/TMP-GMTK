from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ScenarioForm
from .models import Scenario


@login_required
@require_http_methods(["GET", "POST"])
def library(request):
    if request.method == "POST":
        form = ScenarioForm(request.POST, owner=request.user)
        if form.is_valid():
            with transaction.atomic():
                scenario = form.save(commit=False)
                scenario.owner = request.user
                scenario.full_clean()
                scenario.save()
            return HttpResponseRedirect(reverse("scenarios:detail", args=[scenario.pk]))
    else:
        form = ScenarioForm(owner=request.user)
    scenarios = Scenario.objects.filter(owner=request.user).select_related("folder").order_by("-updated_at")
    return render(request, "scenarios/library.html", {"scenarios": scenarios, "form": form})


@login_required
@require_http_methods(["GET"])
def detail(request, pk):
    scenario = get_object_or_404(Scenario.objects.filter(owner=request.user), pk=pk)
    scenes = scenario.scenes.all()
    return render(request, "scenarios/detail.html", {"scenario": scenario, "scenes": scenes})

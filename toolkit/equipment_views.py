"""Owner-scoped CRUD for personal weapons, implants and abilities."""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .equipment_forms import EQUIPMENT_FORMS


def _sections(user):
    return [
        {"kind": kind, "title": title,
         "items": model.objects.filter(owner=user).order_by("name", "id"),
         "create_form": form_class()}
        for kind, (model, form_class, title) in EQUIPMENT_FORMS.items()
    ]


@login_required
def equipment_home(request):
    return render(request, "toolkit/equipment.html", {"sections": _sections(request.user)})


@login_required
def equipment_save(request, kind, item_id=None):
    if kind not in EQUIPMENT_FORMS:
        raise Http404
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    model, form_class, _ = EQUIPMENT_FORMS[kind]
    instance = get_object_or_404(model, pk=item_id, owner=request.user) if item_id else None
    form = form_class(request.POST, instance=instance)
    if not form.is_valid():
        sections = _sections(request.user)
        for section in sections:
            if section["kind"] == kind:
                section["create_form"] = form
        return render(request, "toolkit/equipment.html", {
            "sections": sections,
            "errors": form.errors,
            "error_kind": kind,
        }, status=400)
    item = form.save(commit=False)
    item.owner = request.user
    item.save()
    return redirect("equipment_home")


@login_required
def equipment_delete(request, kind, item_id):
    if kind not in EQUIPMENT_FORMS:
        raise Http404
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    model = EQUIPMENT_FORMS[kind][0]
    get_object_or_404(model, pk=item_id, owner=request.user).delete()
    return redirect("equipment_home")

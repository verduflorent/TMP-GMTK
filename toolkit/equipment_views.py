"""Owner-scoped CRUD for personal weapons, implants and abilities."""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .equipment_forms import EQUIPMENT_FORMS
from catalogue.models import MobWeapon, MobImplant
from catalogue.management.commands.seed_monster_catalogue import WEAPONS, IMPLANTS


def _sections(user):
    return [
        {"kind": kind, "title": title,
         "items": model.objects.filter(owner=user).order_by("name", "id"),
         "create_form": form_class()}
        for kind, (model, form_class, title) in EQUIPMENT_FORMS.items()
    ]


@login_required
def equipment_home(request):
    # The official catalogue is defined in the versioned MONSTER reference.
    # Do not depend on whether the deployment has run the seed command.
    official_weapons = [
        {"name": name, "tier": tier, "profiles": profiles, "hands": hands,
         "range": range_code, "power": power, "aim": aim,
         "property_name": property_name, "property_text": property_text}
        for name, tier, profiles, hands, range_code, power, aim,
            property_name, property_text, _is_control in WEAPONS
    ]
    official_implants = [
        {"name": name, "profiles": profiles,
         "property_name": property_name, "property_text": property_text}
        for name, profiles, property_name, property_text in IMPLANTS
    ]
    return render(request, "toolkit/equipment.html", {
        "sections": _sections(request.user),
        "official_weapons": sorted(official_weapons, key=lambda item: (item["tier"], item["name"])),
        "official_implants": sorted(official_implants, key=lambda item: item["name"]),
    })

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

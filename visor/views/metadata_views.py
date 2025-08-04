import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from visor.forms.metadata_forms import MetadataForm
from visor.models.metadata import Metadata


def gallery(request):
    files = sorted(Path(settings.MEDIA_ROOT).iterdir(), key=lambda p: p.name.lower())
    existing = {m.filename for m in Metadata.objects.all()}
    context = {
        "files": files,
        "existing": existing,
        "mode": request.GET.get("mode", "grid"),
        "all_tags_json": json.dumps(
            list(Metadata.objects.values_list("tags", flat=True).distinct().order_by())
        ),
    }

    if request.headers.get("HX-Request") == "true":  # HTMX call
        return render(request, "_gallery_inner.html", context)
    return render(request, "gallery.html", context)


def edit_metadata(request, filename):
    meta, _ = Metadata.objects.get_or_create(filename=filename)
    if request.method == "POST":
        form = MetadataForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200, content="OK")
    else:
        form = MetadataForm(instance=meta)
    return render(
        request,
        "_metadata_form.html",
        {
            "form": form,
            "filename": filename
        },
    )

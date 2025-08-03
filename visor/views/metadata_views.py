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
    return render(
        request,
        "gallery.html",
        {
            "files": files,
            "existing": existing,
            "all_tags_json": json.dumps(
                list(Metadata.objects.values_list("tags", flat=True).distinct().order_by())
            ),
        },
    )


def edit_metadata(request, filename):
    meta, _ = Metadata.objects.get_or_create(filename=filename)
    if request.method == "POST":
        form = MetadataForm(request.POST, instance=meta)
        print(f"Form data: {request.POST}")
        print("Form errors:", form.errors)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200, content="OK")
    else:
        form = MetadataForm(instance=meta)
    return render(
        request,
        "_metadata_form.html",
        {"form": form, "filename": filename}
    )

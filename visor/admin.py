from django.contrib import admin

from visor.models.metadata import Metadata
from visor.models.tag import Tag


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "title",
        "author",
        "year",
    )
    list_filter = ("author", "year", "museum")
    search_fields = ("filename", "title", "author", "tags")
    readonly_fields = ("filename",)

    fieldsets = (
        (None, {
            "fields": ("filename", "title", "author", "year")
        }),
        ("Details", {
            "fields": ("museum", "material", "source")
        }),
        ("Tags & Description", {
            "fields": ("tags", "description")
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("filename")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("name")

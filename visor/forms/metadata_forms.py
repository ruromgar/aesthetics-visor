from django import forms
from django_select2.forms import ModelSelect2MultipleWidget

from visor.models.metadata import Metadata
from visor.models.tag import Tag


class TagSelectWidget(ModelSelect2MultipleWidget):
    model = Tag
    search_fields = ['name__icontains']

    def create_value(self, value):
        # Optional override: create new tags if not found
        return self.get_queryset().get_or_create(name=value)[0]


class MetadataForm(forms.ModelForm):
    """Form backed by **django-select2** for rich tag input.

    * `filename` - read-only plaintext.
    * `tags` - `ModelMultipleChoiceField` w/ Select2 **tagging** enabled so
      users can type new tags or pick existing ones (searchable dropdown).
    """

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=TagSelectWidget(
            attrs={
                "data-tags": "true",
                "data-placeholder": "Start typing…",
                "data-minimum-input-length": 1,
                "data-allow-clear": "true",
                "data-maximum-selection-length": 10,
                "data-token-separators": '[",", ";"]',
            }
        ),
        help_text="Type to search or create; press Enter to add.",
    )

    class Meta:
        model = Metadata
        fields = [
            "title",
            "author",
            "year",
            "tags",
            "description",
            "museum",
            "material",
            "source",
        ]
        widgets = {
            "year": forms.TextInput(
                attrs={"inputmode": "numeric", "pattern": "[0-9]*"}
            ),
        }

    # ------------------------------------------------------------------
    # Ensure new tags typed in Select2 are created automatically
    # ------------------------------------------------------------------
    # def save(self, commit: bool = True):
    #     instance: Metadata = super().save(commit=False)
    #     if commit:
    #         instance.save()
    #         self.save_m2m()  # save tags relation
    #     # Select2 passes raw strings for new tags
    #     selected_tags = self.cleaned_data.get("tags") or []
    #     for raw_tag in self.data.getlist("tags", []):
    #         if raw_tag.isdigit():
    #             # existing tag primary key
    #             continue
    #         tag_obj, _ = Tag.objects.get_or_create(name=raw_tag.strip())
    #         selected_tags = list(selected_tags) + [tag_obj]
    #     instance.tags.set(selected_tags)
    #     return instance

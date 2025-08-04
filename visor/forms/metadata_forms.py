from django import forms
from django_select2.forms import ModelSelect2TagWidget

from visor.models.metadata import Metadata
from visor.models.tag import Tag


class TagSelectWidget(ModelSelect2TagWidget):
    model = Tag
    search_fields = ['name__icontains']
    queryset = model.objects.all()

    def create_value(self, value):
        self.get_queryset().create(name=value)

    def value_from_datadict(self, data, files, name):
        """Create objects for given non-pimary-key values.

        Return list of all primary keys.
        """
        values = set(super().value_from_datadict(data, files, name))
        id_values = [v for v in values if v.isdigit() and self.queryset.filter(pk=v).exists()]

        pks = self.queryset.filter(**{'pk__in': list(id_values)}).values_list('pk', flat=True)
        pks = set(map(str, pks))
        cleaned_values = list(pks)
        for val in values - pks:
            cleaned_values.append(self.queryset.create(name=val).pk)
        return cleaned_values


class MetadataForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=TagSelectWidget(
            attrs={
                "data-tags": "true",
                "data-minimum-input-length": 1,
                "data-allow-clear": "true",
                "data-maximum-selection-length": 10,
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

from django import forms
from events.models import Event, Category


# ---------------------------------
# Django Standard Form
# ---------------------------------
class EventForm(forms.Form):
    """Standard Event form (non-model version)."""

    name = forms.CharField(max_length=250, label="Event Name")
    description = forms.CharField(widget=forms.Textarea, label="Event Description")
    location = forms.CharField(max_length=200, label="Event Location")
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Event Date"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Event Time"
    )

    category = forms.ChoiceField(choices=[], label="Category")
    participants = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        label="Participants"
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("categories", [])
        participants = kwargs.pop("participants", [])
        super().__init__(*args, **kwargs)

        self.fields['category'].choices = [(cat.id, cat.name) for cat in categories]
        self.fields['participants'].choices = [(p.id, p.name) for p in participants]


# ---------------------------------
# Tailwind Style Mixin
# ---------------------------------
class StyledFormMixin:
    """Mixin to apply Tailwind CSS styles to widgets."""

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self.apply_styled_widgets()

    default_classes = (
        "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm "
        "focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
    )

    def apply_styled_widgets(self):
        """Apply consistent Tailwind CSS classes to all widgets."""
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} resize-none",
                    'placeholder': f"Enter {field.label.lower()}",
                    'rows': 5
                })
            elif isinstance(field.widget, (forms.DateInput, forms.TimeInput)):
                field.widget.attrs.update({
                    "class": self.default_classes
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': self.default_classes})
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': "space-y-2"})
            else:
                field.widget.attrs.update({'class': self.default_classes})


# ---------------------------------
# Django Model Form for Event
# ---------------------------------
class EventModelForm(StyledFormMixin, forms.ModelForm):
    """Model-based Event Form with Tailwind styling."""

    class Meta:
        model = Event
        fields = [
            'name',
            'description',
            'category',
            'location',
            'date',
            'time',
            'participants',
            'asset',
        ]
        widgets = {
            'description': forms.Textarea,
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'participants': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()


# # ---------------------------------
# # Django Model Form for Participant
# # ---------------------------------
# class ParticipantModelForm(StyledFormMixin, forms.ModelForm):
#     """Model-based Participant Form with Tailwind styling."""

#     class Meta:
#         model = 
#         fields = ['name', 'email']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.apply_styled_widgets()



# ---------------------------------
# Django Model Form for Category
# ---------------------------------
class CategoryModelForm(StyledFormMixin, forms.ModelForm):
    """Model-based Category Form with Tailwind styling."""

    class Meta:
        model = Category
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

from django import forms
from .models import ServiceRequest, JobUpdate, Technician
from django.contrib.auth.models import User

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the problem...'}),
        }

class JobUpdateForm(forms.ModelForm):
    class Meta:
        model = JobUpdate
        fields = ['update_text']
        widgets = {
            'update_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter update details...'}),
        }



class AssignTechnicianForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=Technician.objects.select_related('user').all(),
        label="Select Technician"
    )

    class Meta:
        model = ServiceRequest
        fields = ['assigned_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make the dropdown label show full name (or username) plus specialization
        self.fields['assigned_to'].label_from_instance = (
            lambda obj: f"{(obj.user.first_name or obj.user.get_full_name() or obj.user.username).strip()}"
                          + (f" — {obj.specialization}" if obj.specialization else "")
        )
    class Meta:
        model = ServiceRequest
        fields = ['assigned_to']


from django import forms
from .models import NewClubRequest

class NewClubRequestForm(forms.ModelForm):
    class Meta:
        model = NewClubRequest
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError("Club name must be at least 3 characters long.")
        return name
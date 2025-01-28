from django import forms
from .models import News, Event

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter news title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter news content'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter event description'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

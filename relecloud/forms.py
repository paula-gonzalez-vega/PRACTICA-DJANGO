# forms.py
from django import forms
from .models import DestinationReview, CruiseReview

class DestinationReviewForm(forms.ModelForm):
    class Meta:
        model = DestinationReview
        
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 10}),  # Cambiado a 0-10
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class CruiseReviewForm(forms.ModelForm):
    class Meta:
        model = CruiseReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 10}),  # Cambiado a 0-10
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
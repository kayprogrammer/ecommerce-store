from django import forms
from . models import Subscriber

class SubscribeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your Email Address"}))
    
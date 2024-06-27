from django import forms


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your Email Address"}
        )
    )

class MessageForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your Email"}
        )
    )
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject"}
        )
    )
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Message", "rows": 8}
        )
    )

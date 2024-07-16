from django import forms

from apps.shop.choices import PAYMENT_GATEWAY_CHOICES

from .validators import PHONE_REGEX_VALIDATOR

from .models import Country, ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "John Doe"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@email.com"}
        )
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+123 456 789"}
        ),
        validators=[PHONE_REGEX_VALIDATOR],
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123 Street"}
        )
    )
    city = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Good City"}
        )
    )
    state = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Good State"}
        )
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Select a Country",
    )
    zipcode = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "123456"}
        )
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_GATEWAY_CHOICES,
        initial="PAYSTACK",
        widget=forms.RadioSelect(attrs={"class": "custom-control-input"}),
    )

    class Meta:
        model = ShippingAddress
        fields = "__all__"
        exclude = ["id", "user", "created_at", "updated_at"]

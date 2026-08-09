from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Order, UserProfile


User = get_user_model()


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.setdefault("placeholder", field.label)


class RegistrationForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()


class UserUpdateForm(StyledFormMixin, forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already connected to another account.")
        return email


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("full_name", "phone", "address", "city", "postal_code", "profile_image")
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()


class CheckoutForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "customer_name",
            "email",
            "phone",
            "delivery_address",
            "city",
            "postal_code",
            "order_notes",
            "payment_method",
        )
        widgets = {
            "delivery_address": forms.Textarea(attrs={"rows": 3}),
            "order_notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional delivery instructions"}),
            "payment_method": forms.RadioSelect,
        }
        labels = {"delivery_address": "Full delivery address"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

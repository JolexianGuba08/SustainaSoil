from django import forms
from django.core.validators import MaxLengthValidator
from homepage.models import Account


class LoginForm(forms.Form):
    acc_email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent rounded-lg pl-40 '
                     'placeholder:tracking-wide text-accent1 border-accent1',
            'placeholder': 'Email Address',
            'autocomplete': 'off'
        })
    )
    acc_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent pl-40 rounded-lg '
                     'placeholder:tracking-wide text-accent1 border-accent1 ',
            'placeholder': 'Password',
            'autocomplete': 'off'
        })
    )


class SignUpPageForm(forms.ModelForm):
    acc_email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent rounded-lg border-accent1 pl-40 '
                     'placeholder:tracking-wide text-accent1 ',
            'placeholder': 'Email Address',
            'autocomplete': 'off'
        })
    )
    acc_first_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent border-accent1 pl-40 rounded-lg '
                     'placeholder:tracking-wide text-accent1',
            'placeholder': 'First Name',
            'autocomplete': 'off'
        })
    )
    acc_last_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent border-accent1 pl-40 rounded-lg '
                     'placeholder:tracking-wide text-accent1',
            'placeholder': 'Last Name',
            'autocomplete': 'off'
        })
    )
    acc_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'acc_password input input-bordered input-md w-full bg-transparent border-accent1 pl-40 '
                     'rounded-lg'
                     'placeholder:tracking-wide text-accent1',
            'placeholder': 'Password',
            'autocomplete': 'off'
        })
    )
    confirm_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'confirm_password input input-bordered input-md w-full bg-transparent border-accent1 pl-40 '
                     'rounded-lg placeholder:tracking-wide text-accent1',
            'placeholder': 'Confirm Password',
            'autocomplete': 'off'
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("acc_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

    class Meta:
        model = Account
        fields = ['acc_email', 'acc_first_name', 'acc_last_name', 'acc_password']
        exclude = ['acc_id', 'acc_status', 'acc_type', 'acc_profile_img', 'acc_phone', 'acc_date_added',
                   'acc_date_last_updated']


class OTPVerificationForm(forms.Form):
    otp1 = forms.CharField(
        label='',
        validators=[
            MaxLengthValidator(1)
        ],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'maxlength': '1',
            'placeholder': '',
            'required': True,
            'class': 'input input-bordered text-center focus-within:text-center input-md w-full bg-transparent '
                     'border-accent1 pl-40 placeholder:tracking-wide text-accent1 font-bold',
            'id': 'otp1'
        })
    )
    otp2 = forms.CharField(
        label='',
        validators=[
            MaxLengthValidator(1)
        ],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'maxlength': '1',
            'placeholder': '',
            'required': True,
            'class': 'input input-bordered text-center focus-within:text-center input-md w-full bg-transparent '
                     'border-accent1 pl-40 placeholder:tracking-wide text-accent1 font-bold',
            'id': 'otp2'
        })
    )
    otp3 = forms.CharField(
        label='',
        validators=[
            MaxLengthValidator(1)
        ],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'maxlength': '1',
            'placeholder': '',
            'required': True,
            'class': 'input input-bordered text-center focus-within:text-center input-md w-full bg-transparent '
                     'border-accent1 pl-40 placeholder:tracking-wide text-accent1 font-bold',
            'id': 'otp3'
        })
    )
    otp4 = forms.CharField(
        label='',
        validators=[
            MaxLengthValidator(1)
        ],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'maxlength': '1',
            'placeholder': '',
            'required': True,
            'class': 'input input-bordered text-center focus-within:text-center input-md w-full bg-transparent '
                     'border-accent1 pl-40 placeholder:tracking-wide text-accent1 font-bold',
            'id': 'otp4'
        })
    )
    otp5 = forms.CharField(
        label='',
        validators=[
            MaxLengthValidator(1)
        ],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'maxlength': '1',
            'placeholder': '',
            'required': True,
            'class': 'input input-bordered text-center focus-within:text-center input-md w-full bg-transparent '
                     'border-accent1 pl-40 placeholder:tracking-wide text-accent1 font-bold',
            'id': 'otp5'
        })
    )
    otp6 = forms.CharField(
        label='',
        validators=[
            MaxLengthValidator(1)
        ],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'maxlength': '1',
            'placeholder': '',
            'required': True,
            'class': 'input input-bordered text-center focus-within:text-center input-md w-full bg-transparent '
                     'border-accent1 pl-40 placeholder:tracking-wide text-accent1 font-bold',
            'id': 'otp6'
        })
    )


class ForgotPasswordForm(forms.Form):
    acc_email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent rounded-lg pl-40 '
                     'placeholder:tracking-wide text-accent1 border-accent1',
            'placeholder': 'Email Address',
            'autocomplete': 'off'})
    )


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent pl-40 rounded-lg '
                     'placeholder:tracking-wide text-accent1 border-accent1 ',
            'placeholder': 'New Password',
            'autocomplete': 'off'})
    )
    confirm_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered input-md w-full bg-transparent pl-40 rounded-lg '
                     'placeholder:tracking-wide text-accent1 border-accent1 ',
            'placeholder': 'Confirm Password',
            'autocomplete': 'off'})
    )

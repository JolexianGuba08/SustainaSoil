from django import forms

from .models import Account
from .user_context.context_processor import user_context


class EditProfileForm(forms.Form):
    acc_first_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Firstname',
            'required': True,
            'id': 'firstname',
            'class': 'input input-bordered input-md w-[98%] mb-4 bg-transparent text-accent1 pl-40 placeholder:tracking-wide',
        })
    )

    acc_last_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Lastname',
            'required': True,
            'id': 'lastname',
            'class': 'input input-bordered input-md w-[98%] mb-4 bg-transparent text-accent1 pl-40 placeholder:tracking-wide',
        })
    )

    acc_phone = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'inputmode': 'numeric',
            'placeholder': 'Contact No.',
            'maxlength': '11',
            'required': True,
            'id': 'contact',
            'class': 'input input-bordered input-md w-full mb-4 bg-transparent text-accent1 pl-40 placeholder:tracking-wide',
        })
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        initial = kwargs.pop('initial', {})

        super(EditProfileForm, self).__init__(*args, **kwargs)

        # Repopulate fields using initial data
        self.fields['acc_first_name'].widget.attrs['value'] = initial.get('first_name', 'Default First Name')
        self.fields['acc_last_name'].widget.attrs['value'] = initial.get('last_name', 'Default Last Name')
        self.fields['acc_phone'].widget.attrs['value'] = initial.get('phone', 'Default Phone Number')

    class Meta:
        model = Account
        fields = ['acc_first_name', 'acc_last_name', 'acc_phone']
        exclude = ['acc_email', 'acc_password', 'acc_profile_img', 'acc_background_img', 'acc_date_added',
                   'acc_date_last_updated', 'acc_status']


class ChangePasswordForm(forms.Form):
    acc_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'placeholder': 'Old Password',
            'required': True,
            'id': 'old_password',
            'class': 'input input-bordered input-md w-[98%] mb-4 bg-transparent text-accent1 pl-40 placeholder:tracking-wide',
        })
    )

    acc_new_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'placeholder': 'New Password',
            'required': True,
            'id': 'new_password',
            'class': 'input input-bordered input-md w-full mb-4 bg-transparent text-accent1 pl-40 placeholder:tracking-wide',
        })
    )

    acc_confirm_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'placeholder': 'Confirm Password',
            'required': True,
            'id': 'confirm_password',
            'class': 'input input-bordered input-md w-full mb-4 bg-transparent text-accent1 pl-40 placeholder:tracking-wide',
        })
    )

    class Meta:
        model = Account
        fields = ['acc_password', 'acc_new_password', 'acc_confirm_password']
        exclude = ['acc_email', 'acc_first_name', 'acc_last_name', 'acc_phone', 'acc_profile_img', 'acc_background_img',
                   'acc_date_added', 'acc_date_last_updated', 'acc_status']

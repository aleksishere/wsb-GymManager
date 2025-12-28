from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ClassSessions


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    email = forms.EmailField(max_length=254, required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'pesel']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pesel'].widget.attrs.update({
            'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500',
            'placeholder': 'Podaj 11-cyfrowy PESEL'
        })

# core/forms.py

class ClassSessionForm(forms.ModelForm):
    date = forms.DateTimeField(
        label="Data i godzina",
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'shadow border rounded w-full py-2 px-3'
            },
            format='%Y-%m-%dT%H:%M'
        )
    )

    class Meta:
        model = ClassSessions
        fields = ['name', 'date', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow border rounded w-full py-2 px-3'}),
            'capacity': forms.NumberInput(attrs={'class': 'shadow border rounded w-full py-2 px-3'}),
        }
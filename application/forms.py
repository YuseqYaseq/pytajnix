from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=100)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=100)
    password2 = forms.CharField(widget=forms.PasswordInput(), max_length=100, help_text="Repeat your password")
    public_nickname = forms.CharField(max_length=120)

    def clean(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Użytkownik o podanej nazwie już istnieje!')
        
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        
        if password != password2:
            raise ValidationError(u'Podane hasła się nie zgadzają!')
        
        if len(password) < 4:
            raise ValidationError(u'Hasło jest za krótkie!')
        
        return self.cleaned_data


class LectureSelectionForm(forms.Form):
    lecture_id = forms.CharField(max_length=20)


from django.forms import ModelForm
from django import forms

from .models import Room,User,OTP


class MyUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields =['username','email']


       

  

class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields = '__all__'
        exclude=['host','participants']


class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['email','avatar','username']

class OTPCreationForm(ModelForm):
    class Meta:
        model = OTP
        fields = ['email','code']
from django.contrib.auth.forms import AuthenticationForm

from .models import CustomUser

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser

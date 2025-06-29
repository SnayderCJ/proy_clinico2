from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from applications.security.models import User


class EmailAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado que permite login con email
    """

    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 focus:outline-none",
                "placeholder": "correo@ejemplo.com",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 focus:outline-none",
                "placeholder": "Ingrese su contraseña",
            }
        ),
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            # Intentar autenticar con email
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Por favor, introduzca un Email y clave correctos. "
                    "Observe que ambos campos pueden ser sensibles a mayúsculas."
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

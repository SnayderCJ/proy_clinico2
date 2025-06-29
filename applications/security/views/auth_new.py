from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from applications.security.forms.auth import EmailAuthenticationForm


# ----------------- Cerrar Sesion -----------------
@login_required
def signout(request):
    logout(request)
    return redirect("security:signin")


# ----------------- Iniciar Sesion -----------------
def signin(request):
    data = {"title": "Login", "title1": "Inicio de Sesión"}

    if request.method == "GET":
        # Obtener mensajes de éxito de la cola de mensajes
        success_messages = messages.get_messages(request)
        return render(
            request,
            "security/auth/signin.html",
            {
                "form": EmailAuthenticationForm(),
                "success_messages": success_messages,
                **data,
            },
        )
    else:
        form = EmailAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")

        # Si llegamos aquí, hubo un error de autenticación
        return render(
            request,
            "security/auth/signin.html",
            {"form": form, **data},
        )

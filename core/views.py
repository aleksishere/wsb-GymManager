from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone

from .forms import SignUpForm, ProfileForm
from .models import UserMembership


def home(request):
    return render(request, 'base.html')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)  # request.FILES jest kluczowe dla zdjęć!

        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = user.profile
            profile.photo = profile_form.cleaned_data['photo']
            profile.save()

            login(request, user)
            messages.success(request, f"Witaj {user.username}! Twoje konto zostało utworzone.")
            return redirect('home')
    else:
        form = SignUpForm()
        profile_form = ProfileForm()

    return render(request, 'core/register.html', {'form': form, 'profile_form': profile_form})

@login_required
def dashboard(request):
    active_membership = UserMembership.objects.filter(
        user=request.user,
        is_active=True,
        expiration_date__gte=timezone.now().date()
    ).first()

    return render(request, 'core/dashboard.html', {
        'active_membership': active_membership
    })
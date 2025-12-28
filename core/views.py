from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone

from .forms import SignUpForm, ProfileForm
from .models import UserMembership, MembershipType, Visit


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
            profile.pesel = profile_form.cleaned_data['pesel']
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
    recent_visits = request.user.visits.order_by('-entry_time')[:5]
    active_membership = UserMembership.objects.filter(
        user=request.user,
        is_active=True,
        expiration_date__gte=timezone.now().date()
    ).first()

    return render(request, 'core/dashboard.html', {
        'active_membership': active_membership,
        'recent_visits': recent_visits
    })

@login_required
def membership_list(request):
    memberships = MembershipType.objects.all()
    return render(request, 'core/membership_list.html', {'memberships': memberships})

@login_required
def purchase_membership(request, membership_id):
    if request.method == 'POST':
        membership_type = get_object_or_404(MembershipType, id=membership_id)
        UserMembership.objects.create(
            user=request.user,
            membership_type=membership_type
        )
        messages.success(request, f"Gratulacje! Kupiłeś karnet: {membership_type.name}.")
        return redirect('dashboard')
    return redirect('membership_list')

@staff_member_required
def reception_panel(request):
    users = User.objects.filter(is_superuser=False, is_staff=False).select_related('profile')
    users_with_status = []
    for user in users:
        last_visit = user.visits.last()
        in_gym = False
        visit_id = None

        if last_visit and last_visit.exit_time is None:
            in_gym = True
            visit_id = last_visit.id
        users_with_status.append({
            'user': user,
            'in_gym': in_gym,
            'visit_id': visit_id
        })
    return render(request, 'core/reception_panel.html', {'users_with_status': users_with_status})

@staff_member_required
def toggle_visit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    active_visit = Visit.objects.filter(user=user, exit_time__isnull=True).last()
    if active_visit:
        active_visit.exit_time = timezone.now()
        active_visit.save()
        messages.info(request, f"Zakończono wizytę dla {user.username}.")
    else:
        active_membership = UserMembership.objects.filter(
            user=user,
            is_active=True,
            expiration_date__gte=timezone.now().date()
        ).exists()

        if active_membership:
            Visit.objects.create(user=user)
            messages.success(request, f"Rozpoczęto wizytę {user.username}.")
        else:
            messages.error(request, f"Użytkownik {user.username} nie ma aktywnego karnetu.")
    return redirect('reception_panel')
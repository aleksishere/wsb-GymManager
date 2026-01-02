from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
from .validators import validate_pesel

# Rodzaje karnetu (nazwa, cena, czas trwania, ilość wejść)
class MembershipType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa karnetu")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Cena")
    duration_days = models.PositiveIntegerField(verbose_name="Długość (dni)")
    description = models.TextField(verbose_name="Opis korzyści", default="", blank=True)

    entries_per_week = models.PositiveIntegerField(
        verbose_name="Limit wejść w tygodniu",
        null=True,
        blank=True,
        help_text="Zostaw puste dla karnetu bez limitu (Open)"
    )
    def __str__(self):
        limit_str = f"{self.entries_per_week} wejść/tydzień" if self.entries_per_week else "OPEN"
        return f"{self.name} ({limit_str})"

# Karnet użytkownika
class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    membership_type = models.ForeignKey(MembershipType, on_delete=models.SET_NULL, null=True)
    purchase_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)


    def clean(self):
        if self.expiration_date <= self.purchase_date:
            raise ValidationError("Data zakończenia karnetu nie może być wcześniejsza niż data zakupu.")

    def save(self, *args, **kwargs):
        if not self.expiration_date and self.membership_type:
            self.expiration_date = self.purchase_date + timezone.timedelta(days=self.membership_type.duration_days)
        super().save(*args, **kwargs)

# Zajęcia użytkownika
class ClassSessions(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa zajęć")
    date = models.DateTimeField(verbose_name="Data zajęć")
    capacity = models.PositiveIntegerField(verbose_name="Limit miejsc")
    participants = models.ManyToManyField(User, through='Enrollments', related_name='classes')

    def clean(self):
        if self.date and self.date < timezone.now():
            raise ValidationError("Data zajęć nie może być wcześniejsza niż obecna data.")

    def __str__(self):
        return f"{self.name} - {self.date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def spot_count(self):
        return self.participants.count()

    @property
    def is_full(self):
        return self.spot_count >= self.capacity

# Zapisy
class Enrollments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_session = models.ForeignKey(ClassSessions, on_delete=models.CASCADE)
    signup_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'class_session')
        verbose_name = "Zapis"
        verbose_name_plural = "Zapisy"

    def clean(self):
        current_count = self.class_session.participants.count()
        if current_count >= self.class_session.capacity:
            raise ValidationError("Brak wolnych miejsc na te zajęcia.")

        active_membership = UserMembership.objects.filter(
            user=self.user,
            is_active=True,
            expiration_date__gte=timezone.now().date()
        ).exists()
        if not active_membership:
            raise ValidationError("Użytkownik nie ma aktywnego karnetu.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', verbose_name="Zdjęcie profilowe")

    pesel = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_pesel],
        verbose_name="PESEL",
        null=True,
        blank=True
    )

    card_number = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        verbose_name="Numer karty"
    )

    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profil: {self.user.username}"

class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name="Czas wyjścia")
    exit_time = models.DateTimeField(null=True, blank=True, verbose_name="Czas wejścia")

    def save(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(hours=24)
        old_visits = Visit.objects.filter(exit_time__isnull=True, entry_time__lt=cutoff_time)
        for v in old_visits:
            v.exit_time = v.entry_time + timedelta(hours=24)
            v.save()
        super().save(*args, **kwargs)
    @property
    def is_active(self):
        return self.exit_time is None

    def __str__(self):
        return f"Wizyta: {self.user.username} ({self.entry_time.strftime('%Y-%m-%d %H:%M')})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Zabezpieczenie: próba zapisu profilu tylko jeśli istnieje
    if hasattr(instance, 'profile'):
        instance.profile.save()
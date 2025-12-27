from django.contrib import admin
from .models import MembershipType, UserMembership, ClassSessions, Enrollments, Profile

# Rejestracja Typu Karnetu
@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')
    search_fields = ('name',)

# Rejestracja Karnetu Użytkownika
@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'expiration_date', 'is_active')
    list_filter = ('is_active', 'membership_type')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('purchase_date',)

# Rejestracja Zajęć
@admin.register(ClassSessions)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'capacity', 'get_participants_count')
    list_filter = ('date',)
    date_hierarchy = 'date'

    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = 'Zapisanych'

# Rejestracja Zapisów
@admin.register(Enrollments)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_session', 'signup_date')
    list_filter = ('class_session__name',)

# Rejestracja Profilu (zdjęcie)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo')
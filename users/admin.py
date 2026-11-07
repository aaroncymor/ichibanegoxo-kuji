from django.contrib import admin
from .models import User, ClientProfile, PlayerProfile

# Register your models here.
class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    verbose_name_plural = 'Client Profile'
    fk_name = 'user'

class PlayerProfileInline(admin.StackedInline):
    model = PlayerProfile
    can_delete = False
    verbose_name_plural = 'Player Profile'
    fk_name = 'user'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')
    
    def get_inline_instances(self, request, obj=None):
        if obj and obj.role == User.Role.CLIENT_ADMIN:
            return [ClientProfileInline(self.model, self.admin_site)]
        elif obj and obj.role == User.Role.PLAYER:
            return [PlayerProfileInline(self.model, self.admin_site)]
        return []
    
    def get_inlines(self, request, obj):
        if obj and obj.role == User.Role.CLIENT_ADMIN:
            return [ClientProfileInline]
        elif obj and obj.role == User.Role.PLAYER:
            return [PlayerProfileInline]
        return []

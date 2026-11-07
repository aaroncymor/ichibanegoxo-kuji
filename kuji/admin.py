from django.contrib import admin
from .models import KujiSession, KujiPrize
from users.models import User


@admin.register(KujiSession)
class KujiSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_live', 'draw_amount', 'created_by', 'status')
    list_filter = ('is_live', 'status', 'created_by')
    search_fields = ('title', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')

    # 1. Filter lists so clients only see their own sessions
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by__company=request.user.company)

    # 2. Automatically assign the logged-in client as the creator
    def save_model(self, request, obj, form, change):
        if request.user.role not in [User.Role.SUPER_ADMIN, User.Role.CLIENT_ADMIN]:
            raise PermissionError("Only super admins and client admins can create kuji sessions")

        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(KujiPrize)
class KujiPrizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'starting_inventory', 'claimed', 'created_by')
    list_filter = ('tier', 'created_by')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')

    # Filter prizes so clients only see their own prizes
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by__company=request.user.company)

    # Automatically assign the logged-in client as the creator
    def save_model(self, request, obj, form, change):
        if request.user.role not in [User.Role.SUPER_ADMIN, User.Role.CLIENT_ADMIN]:
            raise PermissionError("Only super admins and client admins can create kuji prizes")

        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Restrict the dropdown list of sessions when adding a prize
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "kuji_session" and not (request.user.is_superuser or request.user.role == User.Role.CLIENT_ADMIN):
            kwargs["queryset"] = KujiSession.objects.filter(created_by__company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
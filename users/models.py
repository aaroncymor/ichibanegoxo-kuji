from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
GROUP_ADMIN = 'admins'
GROUP_CLIENT = 'clients'
GROUP_PLAYER = 'players'

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        CLIENT_ADMIN = 'CLIENT_ADMIN', 'Client Admin'
        CLIENT_VIEWER = 'CLIENT_VIEWER', 'Client Viewer'
        PLAYER = 'PLAYER', 'Player'
    
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.PLAYER
    )

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT_ADMIN or self.role == self.Role.CLIENT_VIEWER
    
    @property
    def is_player(self):
        return self.role == self.Role.PLAYER

    @property
    def is_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_client_admin(self):
        return self.role == self.Role.CLIENT_ADMIN

    @property
    def is_client_viewer(self):
        return self.role == self.Role.CLIENT_VIEWER


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    shipping_address_line1 = models.CharField(max_length=255, blank=True, null=True)
    shipping_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    shipping_postal_code = models.CharField(max_length=10, blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"


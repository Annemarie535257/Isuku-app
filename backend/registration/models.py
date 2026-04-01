from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class Province(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Sector(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sectors')
    
    def __str__(self):
        return f"{self.name}, {self.district.name}"


class Cell(models.Model):
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='cells')
    
    def __str__(self):
        return f"{self.name}, {self.sector.name}"


class Village(models.Model):
    name = models.CharField(max_length=100)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='villages')
    
    def __str__(self):
        return f"{self.name}, {self.cell.name}"


class Household(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='household_profile')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    cell = models.ForeignKey(Cell, on_delete=models.SET_NULL, null=True, blank=True)
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude coordinate")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Household"
    
    def has_location(self):
        """Check if household has valid coordinates"""
        return self.latitude is not None and self.longitude is not None


class Collector(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='collector_profile')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude coordinate")
    service_radius = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Service radius in kilometers")
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Collector"
    
    def has_location(self):
        """Check if collector has valid coordinates"""
        return self.latitude is not None and self.longitude is not None


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        blank=True
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ('Super Admin', 'Super Admin'),
            ('Admin', 'Admin'),
            ('Moderator', 'Moderator'),
        ],
        default='Admin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.role}"


class WasteCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=20, default='#000000')
    icon = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='waste_categories/', blank=True, null=True, help_text="Image for waste category")
    
    def __str__(self):
        return self.name
    
    def get_icon(self):
        """Get icon class, with fallback mapping"""
        if self.icon:
            return self.icon
        
        # Default icon mapping based on category name
        icon_map = {
            'Organic Waste': 'fa-leaf',
            'Plastic Waste': 'fa-wine-bottle',
            'Paper Waste': 'fa-file-alt',
            'Glass Waste': 'fa-wine-glass',
            'Metal Waste': 'fa-cog',
            'General Waste': 'fa-trash-alt',
        }
        return icon_map.get(self.name, 'fa-trash-alt')


class WastePickupRequest(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='pickup_requests')
    collector = models.ForeignKey(Collector, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pickups')
    waste_category = models.ForeignKey(WasteCategory, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Scheduled', 'Scheduled'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Pending'
    )
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Pickup location latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Pickup location longitude")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pickup Request #{self.id} - {self.household.user.username} - {self.status}"
    
    def has_location(self):
        """Check if pickup request has valid coordinates"""
        return self.latitude is not None and self.longitude is not None


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


def get_expiry_time():
    """Get expiry time (10 minutes from now)"""
    from django.utils import timezone
    from datetime import timedelta
    return timezone.now() + timedelta(minutes=10)


class OTP(models.Model):
    """Simple OTP model for verification"""
    phoneNumber = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=get_expiry_time)
    
    def __str__(self):
        return f'OTP for {self.phoneNumber}'
    
    class Meta:
        ordering = ['-created_at']

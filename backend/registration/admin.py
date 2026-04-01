from django.contrib import admin
from .models import (
    Province, District, Sector, Cell, Village,
    Household, Collector, Admin,
    WasteCategory, WastePickupRequest, Notification, OTP
)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']
    list_filter = ['province']


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'district']
    list_filter = ['district']


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['name', 'sector']
    list_filter = ['sector']


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'cell']
    list_filter = ['cell']


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'district', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'district', 'province']
    search_fields = ['user__username', 'user__email', 'phone_number']


@admin.register(Collector)
class CollectorAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'license_number', 'is_verified', 'is_available']
    list_filter = ['is_verified', 'is_available']
    search_fields = ['user__username', 'user__email', 'phone_number', 'license_number']


@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'role', 'created_at']
    list_filter = ['role']


@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_code']


@admin.register(WastePickupRequest)
class WastePickupRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'household', 'collector', 'waste_category', 'status', 'scheduled_date', 'created_at']
    list_filter = ['status', 'waste_category', 'created_at']
    search_fields = ['household__user__username', 'collector__user__username']
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phoneNumber', 'otp', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['phoneNumber', 'otp']
    readonly_fields = ['created_at', 'expires_at']

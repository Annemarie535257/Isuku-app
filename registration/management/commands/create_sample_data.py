"""
Management command to create sample data for the waste management system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from registration.models import (
    Province, District, Sector, Cell, Village,
    Household, Collector, Admin, WasteCategory
)


class Command(BaseCommand):
    help = 'Creates sample data for the waste management application'

    def handle(self, *args, **options):
        # Create Provinces and Districts
        kigali, created = Province.objects.get_or_create(name='Kigali')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created province: {kigali.name}'))
        
        nyarugenge, created = District.objects.get_or_create(
            name='Nyarugenge',
            province=kigali
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created district: {nyarugenge.name}'))
        
        # Create Sectors, Cells, and Villages
        sector, created = Sector.objects.get_or_create(
            name='Nyamirambo',
            district=nyarugenge
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created sector: {sector.name}'))
        
        cell, created = Cell.objects.get_or_create(
            name='Cell 1',
            sector=sector
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created cell: {cell.name}'))
        
        village, created = Village.objects.get_or_create(
            name='Village 1',
            cell=cell
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created village: {village.name}'))
        
        # Create Waste Categories
        categories = [
            {'name': 'Organic Waste', 'description': 'Biodegradable waste like food scraps, garden waste', 'color_code': '#4CAF50', 'icon': 'fa-leaf'},
            {'name': 'Plastic Waste', 'description': 'Plastic materials, bottles, containers', 'color_code': '#2196F3', 'icon': 'fa-wine-bottle'},
            {'name': 'Paper Waste', 'description': 'Paper and cardboard materials', 'color_code': '#FF9800', 'icon': 'fa-file-alt'},
            {'name': 'Glass Waste', 'description': 'Glass bottles and containers', 'color_code': '#9C27B0', 'icon': 'fa-wine-glass'},
            {'name': 'Metal Waste', 'description': 'Metal materials, cans, scrap metal', 'color_code': '#607D8B', 'icon': 'fa-cog'},
            {'name': 'General Waste', 'description': 'Non-recyclable and mixed waste', 'color_code': '#795548', 'icon': 'fa-trash-alt'},
        ]
        
        for cat_data in categories:
            category, created = WasteCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created waste category: {category.name}'))
        
        # Create a test household
        household_user, created = User.objects.get_or_create(
            username='household@test.com',
            defaults={
                'email': 'household@test.com',
                'first_name': 'Test',
                'last_name': 'Household'
            }
        )
        if created:
            household_user.set_password('testpass123')
            household_user.save()
            household = Household.objects.create(
                user=household_user,
                phone_number='+250788123456',
                province=kigali,
                district=nyarugenge,
                sector=sector,
                cell=cell,
                village=village,
                street_address='KN 111 ST',
                is_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created test household: {household_user.username} (password: testpass123)'))
        else:
            self.stdout.write(f'Test household already exists: {household_user.username}')
        
        # Create a test collector
        collector_user, created = User.objects.get_or_create(
            username='collector@test.com',
            defaults={
                'email': 'collector@test.com',
                'first_name': 'Test',
                'last_name': 'Collector'
            }
        )
        if created:
            collector_user.set_password('testpass123')
            collector_user.save()
            collector = Collector.objects.create(
                user=collector_user,
                phone_number='+250788654321',
                license_number='COL-001',
                vehicle_number='RAB-1234',
                is_verified=True,
                is_available=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created test collector: {collector_user.username} (password: testpass123)'))
        else:
            self.stdout.write(f'Test collector already exists: {collector_user.username}')
        
        # Create a test admin
        admin_user, created = User.objects.get_or_create(
            username='admin@test.com',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('testpass123')
            admin_user.save()
            admin = Admin.objects.create(
                user=admin_user,
                phone_number='+250788999999',
                role='Super Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Created test admin: {admin_user.username} (password: testpass123)'))
        else:
            self.stdout.write(f'Test admin already exists: {admin_user.username}')
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.WARNING('\nYou can now login with:'))
        self.stdout.write('  Household - Username: household@test.com, Password: testpass123')
        self.stdout.write('  Collector - Username: collector@test.com, Password: testpass123')
        self.stdout.write('  Admin - Username: admin@test.com, Password: testpass123')

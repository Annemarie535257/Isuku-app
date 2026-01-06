"""
Management command to load Rwanda administrative divisions data
"""
from django.core.management.base import BaseCommand
from registration.models import Province, District, Sector, Cell, Village
from registration.data.rwanda_admin_data import RWANDA_ADMIN_DATA


class Command(BaseCommand):
    help = 'Loads Rwanda administrative divisions data (Provinces, Districts, Sectors, Cells, Villages)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load Rwanda administrative data...'))
        
        total_provinces = 0
        total_districts = 0
        total_sectors = 0
        total_cells = 0
        total_villages = 0
        
        for province_name, province_data in RWANDA_ADMIN_DATA.items():
            # Create or get province
            province, created = Province.objects.get_or_create(name=province_name)
            if created:
                total_provinces += 1
                self.stdout.write(self.style.SUCCESS(f'  Created province: {province_name}'))
            
            # Process districts
            for district_name, district_data in province_data.get('districts', {}).items():
                district, created = District.objects.get_or_create(
                    name=district_name,
                    province=province
                )
                if created:
                    total_districts += 1
                    self.stdout.write(self.style.SUCCESS(f'    Created district: {district_name}'))
                
                # Process sectors
                for sector_name, sector_data in district_data.get('sectors', {}).items():
                    sector, created = Sector.objects.get_or_create(
                        name=sector_name,
                        district=district
                    )
                    if created:
                        total_sectors += 1
                    
                    # Process cells
                    for cell_name, villages_list in sector_data.get('cells', {}).items():
                        cell, created = Cell.objects.get_or_create(
                            name=cell_name,
                            sector=sector
                        )
                        if created:
                            total_cells += 1
                        
                        # Process villages
                        for village_name in villages_list:
                            village, created = Village.objects.get_or_create(
                                name=village_name,
                                cell=cell
                            )
                            if created:
                                total_villages += 1
        
        self.stdout.write(self.style.SUCCESS('\n=== Loading Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Provinces: {total_provinces} created'))
        self.stdout.write(self.style.SUCCESS(f'Districts: {total_districts} created'))
        self.stdout.write(self.style.SUCCESS(f'Sectors: {total_sectors} created'))
        self.stdout.write(self.style.SUCCESS(f'Cells: {total_cells} created'))
        self.stdout.write(self.style.SUCCESS(f'Villages: {total_villages} created'))
        self.stdout.write(self.style.SUCCESS('\nRwanda administrative data loaded successfully!'))


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from registration.models import Province, District, Collector


class Command(BaseCommand):
    help = "Create sample collectors for each province and assign them to districts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--per-province",
            type=int,
            default=10,
            help="Number of collectors to create per province (default: 10)",
        )

    def handle(self, *args, **options):
        per_province = options["per_province"]
        total_created = 0

        provinces = Province.objects.prefetch_related("districts").all()
        if not provinces.exists():
            self.stdout.write(self.style.ERROR("No provinces found. Seed provinces and districts first."))
            return

        for province in provinces:
            districts = list(province.districts.all())
            if not districts:
                self.stdout.write(self.style.WARNING(f"Province '{province.name}' has no districts. Skipping."))
                continue

            self.stdout.write(self.style.NOTICE(f"Creating collectors for province: {province.name}"))

            for i in range(per_province):
                district = districts[i % len(districts)]
                username = f"collector_{province.name.lower().replace(' ', '_')}_{i+1}"
                email = f"{username}@example.com"

                user, created_user = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "first_name": "Collector",
                        "last_name": f"{province.name[:3].upper()}{i+1}",
                    },
                )
                if created_user:
                    user.set_password("Collector@123")
                    user.save()

                collector, created_collector = Collector.objects.get_or_create(
                    user=user,
                    defaults={
                        "phone_number": f"+25078{i%10}0000{i+1:02d}",
                        "license_number": f"LIC-{province.id}-{district.id}-{i+1:03d}",
                        "vehicle_number": f"RWA-{province.id}{district.id}{i+1:03d}",
                        "is_verified": True,
                        "province": province,
                        "district": district,
                    },
                )

                if not created_collector:
                    # Update area if collector already existed
                    collector.province = province
                    collector.district = district
                    collector.save(update_fields=["province", "district"])

                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Completed seeding collectors. Total processed: {total_created}"))



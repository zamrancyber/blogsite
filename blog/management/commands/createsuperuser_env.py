import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Create a superuser using environment variables"

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not email or not password:
            self.stdout.write(self.style.ERROR(
                "Environment variables DJANGO_SUPERUSER_USERNAME, "
                "DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD must be set."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Superuser '{username}' already exists. Skipping creation."
            ))
            return

        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{username}' created successfully: {username} - {email}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Failed to create superuser: {str(e)}"
            ))
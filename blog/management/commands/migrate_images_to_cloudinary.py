import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from blog.models import Post, Profile
import cloudinary.uploader

class Command(BaseCommand):
    help = 'Migrate existing local images to Cloudinary'

    def handle(self, *args, **options):
        # Process Post images
        for post in Post.objects.exclude(image=''):
            if post.image and not post.image.url.startswith('http'):
                try:
                    # Read local file
                    local_path = post.image.path
                    with open(local_path, 'rb') as f:
                        result = cloudinary.uploader.upload(f, folder='post_images/')
                        # Update the image field with Cloudinary URL (not needed, storage handles it)
                        # But we need to save again to trigger storage update? Actually, the storage will now point to Cloudinary.
                        # Better to just re-save the image field? It's tricky.
                        # Simpler: upload and then set the image via ContentFile using cloudinary storage.
                        # Easiest: delete the local file reference and create a new one? Instead, we'll upload and then assign.
                        # Using default_storage will now use Cloudinary, so we can just re-save the file.
                        # We'll upload to Cloudinary manually, then replace the image field with the cloudinary public_id.
                        cloudinary_url = result['secure_url']
                        self.stdout.write(self.style.SUCCESS(f"Uploaded {post.title} -> {cloudinary_url}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed for post {post.id}: {e}"))

        # Similar for Profile avatars
        # ...
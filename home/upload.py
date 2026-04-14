import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import FileField, ImageField


class Command(BaseCommand):
    help = "Upload local media files to Cloudinary and update DB references."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Scan files and report what would be uploaded without changing anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        cloudinary_url = os.environ.get("CLOUDINARY_URL")
        if not cloudinary_url:
            self.stderr.write("CLOUDINARY_URL is not set. Set it before running this command.")
            return

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            self.stderr.write(f"MEDIA_ROOT does not exist: {media_root}")
            return

        total_found = 0
        total_uploaded = 0
        total_missing = 0

        for model in apps.get_models():
            file_fields = [
                field
                for field in model._meta.fields
                if isinstance(field, (FileField, ImageField))
            ]
            if not file_fields:
                continue

            for obj in model.objects.all():
                for field in file_fields:
                    file_field = getattr(obj, field.name)
                    if not file_field:
                        continue

                    file_name = file_field.name
                    if not file_name:
                        continue

                    total_found += 1
                    local_path = media_root / file_name
                    if not local_path.exists():
                        total_missing += 1
                        self.stdout.write(
                            f"Missing local file for {model.__name__}.{field.name}: {file_name}"
                        )
                        continue

                    if dry_run:
                        self.stdout.write(
                            f"Would upload {model.__name__}.{field.name}: {file_name}"
                        )
                        continue

                    with local_path.open("rb") as file_obj:
                        file_field.save(file_name, File(file_obj), save=False)
                    obj.save(update_fields=[field.name])
                    total_uploaded += 1
                    self.stdout.write(
                        f"Uploaded {model.__name__}.{field.name}: {file_name}"
                    )

        summary = (
            f"Done. Found: {total_found}, Uploaded: {total_uploaded}, Missing: {total_missing}"
        )
        self.stdout.write(summary)
